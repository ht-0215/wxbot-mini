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
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("wxbot.kb")

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = (".md", ".markdown", ".txt", ".rst", ".tex")
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
    """支持多个根目录（本地 + WSL UNC 路径），每个根独立生成相对 source。"""

    dirs: list[Path] = field(default_factory=lambda: [ROOT / "knowledge"])
    top_k: int = 3
    _chunks: list[Chunk] = field(default_factory=list)
    _stamp: float = 0.0

    # ── 加载 ────────────────────────────────────────────
    def _files(self) -> list[tuple[Path, Path]]:
        out: list[tuple[Path, Path]] = []
        for base in self.dirs:
            if not base.is_dir():
                continue
            for p in sorted(base.rglob("*")):
                if p.suffix.lower() in SUFFIXES and p.is_file():
                    out.append((p, base))
        return out

    def _mtime(self) -> float:
        return max(
            (p.stat().st_mtime for p, _ in self._files()),
            default=0.0,
        )

    def reload(self, force: bool = False) -> None:
        stamp = self._mtime()
        if not force and stamp == self._stamp:
            return
        chunks: list[Chunk] = []
        for p, base in self._files():
            chunks += _split(p, base)
        self._chunks = chunks
        self._stamp = stamp
        log.info("知识库已加载：%d 段（%s）", len(chunks), ", ".join(str(d) for d in self.dirs))

    # ── 检索 ────────────────────────────────────────────
    def search(self, question: str, top_k: int | None = None) -> list[Chunk]:
        self.reload()
        if not self._chunks:
            return []
        k = top_k or self.top_k
        terms = _terms(question)
        scored: list[tuple[int, Chunk]] = []
        for c in self._chunks:
            score = 0
            body_low = c.body.lower()
            title_low = c.title.lower()
            for t in terms:
                tl = t.lower()
                score += title_low.count(tl) * 3 + body_low.count(tl)
            scored.append((score, c))
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


def _terms(question: str) -> list[str]:
    """从问题抽检索词：英文/数字 token + 中文 2-gram。"""
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{1,}|[0-9]{2,}", question)
    cjk = "".join(re.findall(r"[\u4e00-\u9fff]", question))
    grams = [cjk[i:i + 2] for i in range(len(cjk) - 1)] if len(cjk) > 1 else [cjk]
    out = words + grams
    return [t for t in dict.fromkeys(out) if t]
