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
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("wxbot.kb")

ROOT = Path(__file__).resolve().parent.parent
SUFFIXES = (".md", ".markdown", ".txt", ".rst", ".tex")
CODE_SUFFIXES = (".c", ".h", ".dts", ".dtsi")
MAX_CHUNK_CHARS = 1500
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")   # 只在 #/##/### 切段；#### 归入所属小节
MIN_MERGE_CHARS = 200                          # 相邻小段合并阈值，避免章节被切碎

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{1,}|\d{2,}")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CAND_CAP = 3000            # 精算候选上限
PER_SOURCE_CAP = 4         # 同一文件最多贡献段数；与 top_k 对齐，一章答透胜过三段散片
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
        for n, cmd in ((1, "chapter"), (2, "section"), (3, "subsection"),
                       (4, "subsubsection"), (4, "paragraph")):
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


def _cjk_runs(text: str) -> list[str]:
    """提取连续中文串，如 'rgmii link 起不来' → ['起不来']，用于短语加分。"""
    runs = re.findall(r"[一-鿿]{2,}", text)
    # 带连字符/下划线的英文复合词同样有指向性：SPI-NOR、u-boot、phy_nocxn
    runs += [r for r in re.findall(r"[A-Za-z][A-Za-z0-9]*[-_][A-Za-z0-9][\w-]*", text) if len(r) >= 4]
    return runs


# 中文口语 → 文档英文写法：查询侧扩展，弥合中英术语差
ALIAS = {
    "波特率": ["baudrate"], "串口": ["uart"], "自协商": ["auto_negotiate"],
    "千兆": ["1000"], "百兆": ["100"], "烧写": ["burn", "flash"],
    "组播": ["multicast", "mc"], "镜像": ["image"], "带宽": ["bw"],
    "吞吐量": ["throughput"], "端口": ["port"], "寄存器": ["reg"],
}


def _tokens_of(text: str, *, limit: int = 0) -> set[str]:
    """英文/数字 token + 子词 + 中文 2-gram + 别名扩展（正文只取前 limit 字防爆炸）。"""
    toks: set[str] = {t.lower() for t in WORD_RE.findall(text)}
    for t in list(toks):
        toks |= _subtokens(t)
    body = text if not limit else text[:limit]
    cjk = "".join(CJK_RE.findall(body))
    toks |= {cjk[j:j + 2] for j in range(len(cjk) - 1)}
    for zh, ens in ALIAS.items():
        if zh in text:
            toks |= {e.lower() for e in ens}
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
    hybrid: bool = True                 # BM25 ∪ 向量 重排；模型缺失自动退回纯 BM25
    _chunks: list[Chunk] = field(default_factory=list)
    _index: dict[str, set[int]] = field(default_factory=dict)   # token → chunk 下标
    _lens: list[int] = field(default_factory=list)              # 每段 token 数
    _avg_len: float = 1.0
    _stamp: float = 0.0
    _checked_at: float = 0.0
    _vec: object = None                 # VectorIndex，惰性创建

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
        """同步重载（首次/手动）。运行期建议走 refresh() 的后台路径。"""
        now = time.monotonic()
        if not force and self._chunks and now - self._checked_at < RELOAD_TTL:
            return                       # TTL 内直接用内存索引
        stamp = self._mtime()
        self._checked_at = now
        if not force and stamp == self._stamp:
            return
        self._build(stamp)

    def refresh(self) -> None:
        """后台线程用：扫 mtime，变了才重建，不受 TTL 限制。"""
        try:
            stamp = self._mtime()
            self._checked_at = time.monotonic()
            if stamp != self._stamp:
                self._build(stamp)
        except Exception as exc:  # noqa: BLE001
            log.warning("知识库后台刷新失败: %s", exc)

    def _build(self, stamp: float) -> None:
        cached = self._load_bm25_cache(stamp)
        if cached is not None:
            self._chunks, self._index, self._lens, self._avg_len = cached
            self._stamp = stamp
            log.info("BM25 索引缓存命中：%d 段 / %d 词", len(self._chunks), len(self._index))
            if self.hybrid:
                self._rebuild_vectors(self._chunks)
            return
        chunks: list[Chunk] = []
        for p, base, is_code in self._files():
            chunks += _split_code(p, base) if is_code else _split(p, base)

        index: dict[str, set[int]] = {}
        lens: list[int] = []
        dir_cache: dict[str, set[str]] = {}     # 目录段 token 按 source 缓存
        for i, c in enumerate(chunks):
            toks = _tokens_of(c.title) | _tokens_of(c.body, limit=4000)
            stem = Path(c.source).stem
            toks |= _tokens_of(stem)              # 文件名可直接搜
            # 目录段也进索引：doc_kd5886-dev → kd5886，型号查询优先命中对应目录
            dt = dir_cache.get(c.source)
            if dt is None:
                dt = set()
                for part in Path(c.source).parts[:-1]:
                    if part != "common":
                        dt |= _tokens_of(Path(part).stem)
                dir_cache[c.source] = dt
            toks |= dt
            lens.append(len(toks))
            for tok in toks:
                index.setdefault(tok, set()).add(i)
        # 全部算完再一次性切换，后台重建期间查询读到的仍是旧一致快照
        self._chunks, self._index, self._lens = chunks, index, lens
        self._avg_len = (sum(lens) / len(lens)) if lens else 1.0
        self._stamp = stamp
        roots = [str(d) for d in self.dirs] + [f"{d}(code)" for d in self.code_dirs]
        log.info("知识库已加载：%d 段 / %d 词（%s）", len(chunks), len(index), ", ".join(roots))
        self._save_bm25_cache()
        if self.hybrid:
            self._rebuild_vectors(chunks)

    # ── BM25 索引持久化：冷启动免 120s 重建 ───────────────
    def _cache_key(self) -> str:
        import hashlib
        h = hashlib.sha1()
        for d in list(self.dirs) + list(self.code_dirs):
            h.update(str(d).encode("utf-8"))
        return h.hexdigest()[:12]

    def _cache_path(self, stamp: float | None = None) -> Path:
        s = self._stamp if stamp is None else stamp
        return ROOT / f".bm25_cache_{self._cache_key()}_{int(s)}.pkl"

    def _load_bm25_cache(self, stamp: float):
        """同 stamp 的缓存文件命中则返回四元组，否则 None。"""
        import pickle
        p = self._cache_path(stamp)
        if not p.exists():
            return None
        try:
            with p.open("rb") as fh:
                chunks, index, lens, avg = pickle.load(fh)
            if len(chunks) != len(lens):
                return None
            return chunks, index, lens, avg
        except Exception as exc:  # noqa: BLE001
            log.debug("BM25 缓存读取失败: %s", exc)
            return None

    def _save_bm25_cache(self) -> None:
        import pickle
        try:
            p = self._cache_path()
            for old in ROOT.glob(f".bm25_cache_{self._cache_key()}_*.pkl"):
                if old != p:
                    old.unlink(missing_ok=True)
            with p.open("wb") as fh:
                pickle.dump((self._chunks, self._index, self._lens, self._avg_len),
                            fh, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as exc:  # noqa: BLE001
            log.debug("BM25 缓存写入失败: %s", exc)

    def _rebuild_vectors(self, chunks: list[Chunk]) -> None:
        """BM25 重建后同步向量索引：优先读缓存，签名不符才后台编码。

        只编码文档段（md/tex/txt，约数百段）；代码段量大且标识符密集，
        BM25 已够，向量置零不参与语义路。
        """
        try:
            from bot.vector import VectorIndex
            if self._vec is None:
                self._vec = VectorIndex()
            keys = [f"{c.source}#{i}" for i, c in enumerate(chunks)]
            if self._vec.load_cache(keys):
                threading.Thread(target=self._vec._ensure_model, daemon=True).start()
                return                      # 后台预热模型，首问不再等加载
            rows, texts = [], []
            for i, c in enumerate(chunks):
                if c.source.lower().endswith((".c", ".h", ".dts", ".dtsi")):
                    continue
                rows.append(i)
                texts.append(c.title + "。" + c.body[:600])
            th = threading.Thread(target=self._vec.build, args=(keys, texts, rows), daemon=True)
            th.start()          # 编码耗时放在后台，不阻塞启动
        except Exception as exc:  # noqa: BLE001
            log.debug("向量索引跳过: %s", exc)
            self._vec = None

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
        q_runs = [r for r in _cjk_runs(question) if len(r) >= 2]
        # 区分度权重：较长 ASCII 标识符（gs8611/kd5886）远比中文 2-gram 指向性强；
        # 3 字符以下的碎片（nor/sf）容易撞 define 名，不加权。
        wt = {t: (2.0 if re.match(r"[a-z0-9]", t) and len(t) >= 4 else 1.0) for t in qt}
        for i in cand:
            c = self._chunks[i]
            body_low, title_low = c.body.lower(), c.title.lower()
            path_low = c.source.lower()
            stem_low = Path(c.source).stem.lower()
            score = 0.0
            for t in qt:
                idf = self._idf(t, n)
                if idf <= 0:
                    continue
                tf = min(body_low.count(t), 8)
                denom = tf + _K1 * (1 - _B + _B * self._lens[i] / self._avg_len)
                score += wt[t] * (idf * tf * (_K1 + 1) / denom if denom else 0.0)
                if t in title_low:
                    score += wt[t] * idf * 2.0
                # 文件名命中：gs8611.c 这类指向性强；短词(spi)只轻加权，防霸屏
                if t in stem_low:
                    score += wt[t] * idf * (3.0 if len(t) >= 5 else 1.2)
                # 目录命中：问 kd5886 优先 doc_kd5886-dev/，压过同名 5128 文档
                elif len(t) >= 4 and t in path_low:
                    score += wt[t] * idf * 2.0
            # 短语命中加分：长短语拆 3 字滑窗，命中越多越像答案
            for r in q_runs:
                if len(r) <= 4:
                    wins = [r]
                else:
                    wins = [r[j:j + 3] for j in range(len(r) - 2)]
                w = min(len(r) * 0.8, 4.0) / len(wins)
                for win in wins:
                    if win in c.title:
                        score += w
                    elif win in c.body:
                        score += w * (1.0 if len(r) >= 4 else 0.4)
            # 过短段（目录式概述）轻惩罚：让带实际内容的长文档段排前。
            # 但短段若含查询里的 ASCII 标识符（readme 含 ddr/uboot），说明就是答案，不罚。
            ascii_toks = [t for t in qt if re.match(r"[a-z0-9]", t) and len(t) >= 3]
            if len(c.body) < 140:
                if not any(t in body_low for t in ascii_toks):
                    score *= 0.6
            elif len(c.body) >= 400:
                score *= 1.1
            # 中文问句优先文档段：代码碎片(数组定义等)常撞标识符但非答案
            if q_runs and c.source.lower().endswith((".md", ".tex", ".txt", ".rst")):
                score *= 1.25
            if score > 0:
                scored.append((score, i))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        # ③ 混合重排：BM25 名次 + 向量余弦，两路互为兜底
        merged = self._hybrid_merge(scored, question)
        # ④ 邻段续接：命中的段之后紧跟同文档下一段——章节细节常写在下一小节
        order: list[int] = []
        seen_i: set[int] = set()
        for i in merged:
            if i in seen_i:
                continue
            seen_i.add(i)
            order.append(i)
            nxt = i + 1
            if (nxt < len(self._chunks)
                    and self._chunks[nxt].source == self._chunks[i].source
                    and nxt not in seen_i):
                seen_i.add(nxt)
                order.append(nxt)
        # ⑤ 来源多样性：同文件最多 max(PER_SOURCE_CAP, k) 段
        cap = max(PER_SOURCE_CAP, k)
        hits: list[Chunk] = []
        per_source: dict[str, int] = {}
        for i in order:
            c = self._chunks[i]
            cnt = per_source.get(c.source, 0)
            if cnt >= cap:
                continue
            per_source[c.source] = cnt + 1
            hits.append(c)
            if len(hits) >= k:
                return hits
        if hits:
            return hits
        # 全无命中：返回空而不是塞无关首段——让模型如实说"资料未覆盖"
        return []

    def _hybrid_merge(self, scored: list[tuple[float, int]], question: str) -> list[int]:
        """RRF 名次融合：score = Σ 1/(60+rank)，BM25 与向量两路等权；
        任一路缺失则直接用另一路。名次融合不受两路分数量纲差异影响。"""
        bm = [i for _, i in scored[:40]]
        vec: list[int] = []
        if self.hybrid and self._vec is not None:
            seen: set[int] = set()
            for i, _sim in self._vec.top(question, len(self._chunks), k=20):
                if 0 <= i < len(self._chunks) and i not in seen:
                    seen.add(i)
                    vec.append(i)
        if not bm:
            return vec
        if not vec:
            return bm
        fused: dict[int, float] = {}
        for rank, i in enumerate(bm):
            fused[i] = fused.get(i, 0.0) + 1.0 / (60 + rank)
        for rank, i in enumerate(vec):
            fused[i] = fused.get(i, 0.0) + 1.0 / (60 + rank)
        return sorted(fused, key=lambda i: -fused[i])

    def context_block(self, question: str) -> str:
        chunks = self.search(question)
        if not chunks:
            return ""
        return "【知识库参考】\n" + "\n\n".join(c.text for c in chunks)


def _split(path: Path, base: Path) -> list[Chunk]:
    """按 #~### 标题切段；更深层级(####)留在所属小节内。
    不足 MIN_MERGE_CHARS 的小节并入前一段，避免章节被切碎。tex 先转轻 markdown。"""
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
        if not body:
            return
        body = body[:MAX_CHUNK_CHARS]
        if chunks and len(body) < MIN_MERGE_CHARS:
            prev = chunks[-1]
            if len(prev.body) + len(body) <= MAX_CHUNK_CHARS:
                keep = (title + "\n") if title and title != prev.title else ""
                chunks[-1] = Chunk(prev.source, prev.title,
                                   prev.body + "\n" + keep + body)
                return
        chunks.append(Chunk(source=source, title=title, body=body))

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
    last_sig = ""      # 最近一条疑似函数签名行，供独行 "{" 命名用

    def flush() -> None:
        nonlocal buf
        body = "\n".join(buf).strip()
        if len(body) > 30:
            chunks.append(Chunk(source=source, title=title, body=body[:MAX_CHUNK_CHARS * 2]))
        buf = []

    def name_of(line: str) -> str:
        m = re.match(r"[A-Za-z_][A-Za-z0-9_ \*]*?([A-Za-z_]\w*)\s*[\({]", line)
        return m.group(1) if m else line[:40]

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith(("*", "//", "#include")) and not line[:1].isspace():
            if stripped == "{" and last_sig:
                flush()                       # 多行签名：名字在上一行
                title = name_of(last_sig)
            elif "{" in stripped or stripped.startswith(("struct ", "typedef ", "#define ", "int ", "void ", "static ")):
                flush()
                title = name_of(stripped)
        if stripped and not stripped.startswith(("//", "/*")):
            last_sig = stripped if re.match(r"[A-Za-z_][\w \*]*\(?", stripped) else last_sig
        buf.append(line)
        if len(buf) > 120:
            flush()
    flush()
    return chunks
