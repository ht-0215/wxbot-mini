"""知识库：从 knowledge/ 目录读 md/txt，按关键词命中挑选段落注入提问。

轻量实现（无向量依赖）：
  1. 每个文件按 ## / ### 标题切段，段落标题 + 正文构成一个 chunk
  2. 用问题里的词对 chunk 做字面命中计分（标题命中权重高）
  3. 取得分最高的 top-k 段拼进提问；全无命中则取每文件首段兜底

支持子目录递归；改文件即生效（按 mtime 缓存，下次提问自动重载）。
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("wxbot.kb")

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = (".md", ".markdown", ".txt", ".rst", ".tex")
CODE_SUFFIXES = (".c", ".h", ".dts", ".dtsi")
ALL_SUFFIXES = SUFFIXES + CODE_SUFFIXES
MAX_CHUNK_CHARS = 900
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def _tex_to_md(text: str) -> str:
    """LaTeX → 轻 markdown：章节命令转标题，去注释与排版命令。"""
    out = []
    for line in text.splitlines():
        line = line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("%%%"):
            continue
        for n, cmd in ((1, "chapter"), (2, "section"), (3, "subsection")):
            m = re.match(rf"\\{cmd}\*?\{{(.+?)\}}\s*$", stripped)
            if m:
                stripped = "#" * n + " " + m.group(1)
                break
        else:
            stripped = re.sub(r"\\(newpage|clearpage|bibliography\{[^}]*\}|maketitle)\b", "", stripped)
            stripped = re.sub(r"^%\s?", "", stripped)
        if stripped.strip():
            out.append(stripped)
    return "\n".join(out)


@dataclass
class Chunk:
    source: str
    title: str
    body: str

    @property
    def text(self) -> str:
        head = f"[{self.source} › {self.title}]" if self.title else f"[{self.source}]"
        return f"{head}\n{self.body.strip()}"


@dataclass
class KnowledgeBase:
    """多根知识库：dirs 收文档（md/txt/tex），code_dirs 收源码子集（c/h/dts）。

    code_dirs 建议只挂关心的子目录（如 arch/csky、drivers/net/phy），
    整棵内核树文件过多会拖慢首次加载。
    """

    dirs: list[Path] = field(default_factory=lambda: [ROOT / "knowledge"])
    code_dirs: list[Path] = field(default_factory=list)
    top_k: int = 3
    _chunks: list[Chunk] = field(default_factory=list)
    _index: dict[str, set[int]] = field(default_factory=dict)   # token → chunk 下标
    _stamp: float = 0.0
    _checked_at: float = 0.0     # 上次 mtime 扫描时刻（UNC walk 慢，TTL 内跳过）

    # ── 加载 ────────────────────────────────────────────
    def _files(self) -> list[tuple[Path, Path, bool]]:
        out: list[tuple[Path, Path, bool]] = []
        for base in self.dirs:
            if base.is_dir():
                out += [(p, base, False) for p in sorted(base.rglob("*"))
                        if p.suffix.lower() in SUFFIXES and p.is_file()]
        for base in self.code_dirs:
            if base.is_dir():
                out += [(p, base, True) for p in sorted(base.rglob("*"))
                        if p.suffix.lower() in CODE_SUFFIXES and p.is_file()]
        return out

    def _mtime(self) -> float:
        return max((p.stat().st_mtime for p, _, _ in self._files()), default=0.0)

    def reload(self, force: bool = False) -> None:
        now = time.monotonic()
        if not force and self._chunks and now - self._checked_at < 30:
            return                      # UNC 遍历慢，30s TTL 内跳过 mtime 检查
        stamp = self._mtime()
        self._checked_at = now
        if not force and stamp == self._stamp:
            return
        chunks: list[Chunk] = []
        for p, base, is_code in self._files():
            chunks += _split_code(p, base) if is_code else _split(p, base)
        self._chunks = chunks
        # 倒排索引：token → chunk 下标，检索只扫候选段而不是全库
        index: dict[str, set[int]] = {}
        for i, c in enumerate(chunks):
            tokens = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}|\d{2,}", c.title)}
            body_low = c.body.lower()
            for tok in {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}|\d{2,}", body_low)}:
                tokens.add(tok)
            cjk = "".join(re.findall(r"[\u4e00-\u9fff]", c.title + c.body[:2000]))
            tokens |= {cjk[j:j + 2] for j in range(len(cjk) - 1)}
            for tok in tokens:
                index.setdefault(tok, set()).add(i)
        self._index = index
        self._stamp = stamp
        roots = [str(d) for d in self.dirs] + [f"{d}(code)" for d in self.code_dirs]
        log.info("知识库已加载：%d 段（%s）", len(chunks), ", ".join(roots))

    # ── 检索 ────────────────────────────────────────────
    def search(self, question: str, top_k: int | None = None) -> list[Chunk]:
        self.reload()
        if not self._chunks:
            return []
        k = top_k or self.top_k
        terms = _terms(question)
        # 候选 = 命中任一词的段；按倒排表从小到大取，总候选封顶避免高频词拖垮精算
        postings = sorted(
            (self._index.get(t.lower(), set()) for t in terms),
            key=len,
        )
        cand: set[int] = set()
        for p in postings:
            if not p:
                continue
            if len(cand) + len(p) > 3000 and cand:
                break
            cand |= p
        scored: list[tuple[int, Chunk]] = []
        for i in cand:
            c = self._chunks[i]
            score = 0
            body_low = c.body.lower()
            title_low = c.title.lower()
            for t in terms:
                tl = t.lower()
                score += title_low.count(tl) * 3 + body_low.count(tl)
            scored.append((score, c))
        scored.sort(key=lambda pair: pair[0], reverse=True)   # 高分段优先
        hit = [c for s, c in scored if s > 0]
        if not hit:                        # 无命中：每个文件首段兜底
            seen: set[str] = set()
            hit = [c for c in self._chunks if not (c.source in seen or seen.add(c.source))]
        return hit[:k]

    def context_block(self, question: str) -> str:
        chunks = self.search(question)
        if not chunks:
            return ""
        return "【知识库参考】\n" + "\n\n".join(c.text for c in chunks)


def _split(path: Path, base: Path) -> list[Chunk]:
    """按标题切段；无标题的文件整体一段。tex 先转轻 markdown 再切。"""
    source = path.relative_to(base).as_posix()
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".tex":
        raw = _tex_to_md(raw)
    lines = raw.splitlines()
    chunks: list[Chunk] = []
    title, buf = "", []

    def flush() -> None:
        body = "\n".join(buf).strip()
        if body:
            chunks.append(Chunk(source=source, title=title, body=body[:MAX_CHUNK_CHARS]))

    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            flush()
            title, buf = m.group(2).strip(), []
        else:
            buf.append(line)
    flush()
    if not chunks:
        body = "\n".join(lines).strip()
        if body:
            chunks.append(Chunk(source=source, title="", body=body[:MAX_CHUNK_CHARS]))
    return chunks


def _split_code(path: Path, base: Path) -> list[Chunk]:
    """源码切段：以函数定义/顶层声明为界，注释块跟随其后代码。

    比 md 规则糙一些，但能把一个大 .c 拆成按函数的段，命中后返回的是相关函数
    上下文而不是整文件头 900 字。
    """
    source = path.relative_to(base).as_posix()
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    chunks: list[Chunk] = []
    buf: list[str] = []
    title = ""

    def flush() -> None:
        nonlocal buf
        body = "\n".join(buf).strip()
        if len(body) > 30:
            chunks.append(Chunk(source=source, title=title, body=body[:MAX_CHUNK_CHARS * 2]))
        buf = []

    for line in lines:
        stripped = line.strip()
        # 顶层函数/结构体/宏起始 → 开新段
        if stripped and not stripped.startswith(("*", "//", "#include")) and not line[:1].isspace():
            if "{" in stripped or stripped.startswith(("struct ", "typedef ", "#define ", "int ", "void ", "static ")):
                flush()
                name = re.match(r"[A-Za-z_][A-Za-z0-9_ \*]*?([A-Za-z_]\w*)\s*[\({]", stripped)
                title = name.group(1) if name else stripped[:40]
        buf.append(line)
        if len(buf) > 120:          # 单段行数上限，避免超长
            flush()
    flush()
    return chunks


def _terms(question: str) -> list[str]:
    """从问题抽检索词：英文/数字 token + 中文 2-gram。"""
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}|[0-9]{2,}", question)
    cjk = "".join(re.findall(r"[\u4e00-\u9fff]", question))
    grams = [cjk[i:i + 2] for i in range(len(cjk) - 1)] if len(cjk) > 1 else [cjk]
    out = words + grams
    return [t for t in dict.fromkeys(out) if t]
