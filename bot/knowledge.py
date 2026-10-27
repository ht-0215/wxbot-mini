"""知识库：多根目录（本地 + WSL UNC）文档/源码检索，BM25 风格计分。

文档（md/txt/rst/tex）按 ##/### 标题切段；tex 先转轻 markdown。
源码（c/h/dts/dtsi）按顶层函数/宏切段，标题取函数名。

检索两级：倒排索引出候选（含文件名、标识符子词），候选内 BM25 精算——
稀有词（kd5860）IDF 权重高于高频词（配置），tf 饱和 + 段长归一化。
结果按得分排序，同一来源最多两格，避免单文件霸屏。

缓存：mtime 变化才重建；UNC 遍历慢，300s TTL 内跳过检查，启动 force 一次。
"""
from __future__ import annotations

import logging
import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("wxbot.kb")

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = (".md", ".markdown", ".txt", ".rst", ".tex")
CODE_SUFFIXES = (".c", ".h", ".dts", ".dtsi")
MAX_CHUNK_CHARS = 900
HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,}|\d{2,}")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CAND_CAP = 3000            # 精算候选上限
PER_SOURCE_CAP = 2         # 同一文件最多贡献段数
RELOAD_TTL = 300.0         # UNC mtime 检查节流（秒）

# BM25 参数（经验值，与 rank_bm25 默认一致）
_K1, _B = 1.5, 0.75


def _tex_to_md(text: str) -> str:
    """LaTeX → 轻 markdown：章节命令转标题，去注释与排版命令。"""
    out = []
    for line in text.splitlines():
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


def _subtokens(token: str) -> set[str]:
    """标识符拆子词：phy_nocxn → {phy, nocxn}；camelCase 同理。"""
    parts = [p for p in re.split(r"[_\-]|(?<=[a-z0-9])(?=[A-Z])", token) if len(p) > 1]
    return {p.lower() for p in parts} if len(parts) > 1 else set()


def _tokens_of(text: str, *, limit: int = 0) -> set[str]:
    """英文/数字 token + 子词 + 中文 2-gram（正文只取前 limit 字防爆炸）。"""
    toks: set[str] = {t.lower() for t in WORD_RE.findall(text)}
    for t in list(toks):
        toks |= _subtokens(t)
    if limit:
        text = text[:limit]
    cjk = "".join(CJK_RE.findall(text))
    toks |= {cjk[j:j + 2] for j in range(len(cjk) - 1)}
    return toks


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
    _lens: list[int] = field(default_factory=list)              # 每段 token 数
    _avg_len: float = 1.0
    _stamp: float = 0.0
    _checked_at: float = 0.0

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
        if not force and self._chunks and now - self._checked_at < RELOAD_TTL:
            return                       # TTL 内直接用内存索引
        stamp = self._mtime()
        self._checked_at = now
        if not force and stamp == self._stamp:
            return
        chunks: list[Chunk] = []
        for p, base, is_code in self._files():
            chunks += _split_code(p, base) if is_code else _split(p, base)
        self._chunks = chunks

        index: dict[str, set[int]] = {}
        lens: list[int] = []
        for i, c in enumerate(chunks):
            toks = _tokens_of(c.title) | _tokens_of(c.body, limit=4000)
            stem = Path(c.source).stem
            toks |= _tokens_of(stem)              # 文件名可直接搜
            lens.append(len(toks))
            for tok in toks:
                index.setdefault(tok, set()).add(i)
        self._index = index
        self._lens = lens
        self._avg_len = (sum(lens) / len(lens)) if lens else 1.0
        self._stamp = stamp
        roots = [str(d) for d in self.dirs] + [f"{d}(code)" for d in self.code_dirs]
        log.info("知识库已加载：%d 段 / %d 词（%s）", len(chunks), len(index), ", ".join(roots))

    # ── 计分 ────────────────────────────────────────────
    def _idf(self, term: str, n_chunks: int) -> float:
        df = len(self._index.get(term, ()))
        if not df:
            return 0.0
        return math.log(1 + (n_chunks - df + 0.5) / (df + 0.5))

    def search(self, question: str, top_k: int | None = None) -> list[Chunk]:
        self.reload()
        if not self._chunks:
            return []
        k = top_k or self.top_k
        n = len(self._chunks)
        qt = _tokens_of(question)
        # ① 倒排出候选：按 posting 小→大合并，封顶 CAND_CAP
        postings = sorted((self._index.get(t, set()) for t in qt), key=len)
        cand: set[int] = set()
        for p in postings:
            if not p:
                continue
            if cand and len(cand) + len(p) > CAND_CAP:
                break
            cand |= p
        # ② BM25 精算：idf × tf 饱和 × 长度归一，标题命中加倍
        scored: list[tuple[float, Chunk]] = []
        for i in cand:
            c = self._chunks[i]
            body_low, title_low = c.body.lower(), c.title.lower()
            score = 0.0
            for t in qt:
                idf = self._idf(t, n)
                if idf <= 0:
                    continue
                tf = min(body_low.count(t), 8)
                denom = tf + _K1 * (1 - _B + _B * self._lens[i] / self._avg_len)
                score += idf * tf * (_K1 + 1) / denom if denom else 0.0
                if t in title_low:
                    score += idf * 2.0
            if score > 0:
                scored.append((score, c))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        # ③ 来源多样性：同文件最多 PER_SOURCE_CAP 段
        hits: list[Chunk] = []
        per_source: dict[str, int] = {}
        for _, c in scored:
            cnt = per_source.get(c.source, 0)
            if cnt >= PER_SOURCE_CAP:
                continue
            per_source[c.source] = cnt + 1
            hits.append(c)
            if len(hits) >= k:
                return hits
        if hits:
            return hits
        # ④ 全无命中：每个文件首段兜底
        seen: set[str] = set()
        return [c for c in self._chunks if not (c.source in seen or seen.add(c.source))][:k]

    def context_block(self, question: str) -> str:
        chunks = self.search(question)
        if not chunks:
            return ""
        return "【知识库参考】\n" + "\n\n".join(c.text for c in chunks)


def _split(path: Path, base: Path) -> list[Chunk]:
    """按标题切段；无标题的文件整体一段。tex 先转轻 markdown 再切。"""
    source = path.relative_to(base).as_posix()
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
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
    """源码切段：以函数定义/顶层声明为界，注释块跟随其后代码。"""
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
        if stripped and not stripped.startswith(("*", "//", "#include")) and not line[:1].isspace():
            if "{" in stripped or stripped.startswith(("struct ", "typedef ", "#define ", "int ", "void ", "static ")):
                flush()
                name = re.match(r"[A-Za-z_][A-Za-z0-9_ \*]*?([A-Za-z_]\w*)\s*[\({]", stripped)
                title = name.group(1) if name else stripped[:40]
        buf.append(line)
        if len(buf) > 120:
            flush()
    flush()
    return chunks
