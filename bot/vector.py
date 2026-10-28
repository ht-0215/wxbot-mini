"""向量检索：bge-small-zh-v1.5 语义嵌入 + numpy 余弦，与 BM25 混合重排。

设计：
  - 整库编码一次存 .npz（float16），mtime 变了增量重编变化的段
  - 查询：BM25 候选 ∪ 向量 top-N → 加权重排 → top_k
  - sentence-transformers 缺失或模型下载失败时自动退回纯 BM25，不影响主链路

模型约 100MB，首次加载时从 hf 镜像下载；离线环境把 BAAI/bge-small-zh-v1.5
放到 ~/.cache/huggingface/ 即可。
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np

log = logging.getLogger("wxbot.vec")

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".vec_cache.npz"
MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def _model_cached() -> bool:
    """hf 缓存里是否已有该模型（config.json + 权重目录存在即可）。"""
    import os
    home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    d = home / "hub" / f"models--{MODEL_NAME.replace('/', '--')}"
    return (d / "snapshots").is_dir() and any((d / "snapshots").glob("*/config.json"))


class VectorIndex:
    def __init__(self, dim_hint: int = 512) -> None:
        self.model = None
        self.vecs: np.ndarray | None = None      # (n, dim) float32，已归一化
        self.sig: str = ""                        # chunks 签名，判断增量
        self.dim_hint = dim_hint

    # ── 模型 ────────────────────────────────────────────
    def _ensure_model(self) -> bool:
        if self.model is not None:
            return True
        try:
            import os
            os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")  # 国内镜像兜底
            if os.environ.get("HF_HOME") or _model_cached():
                os.environ.setdefault("HF_HUB_OFFLINE", "1")   # 已有本地缓存就不再联网核对
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
            self.model = SentenceTransformer(MODEL_NAME)
            log.info("嵌入模型已加载: %s", MODEL_NAME)
            return True
        except Exception as exc:  # noqa: BLE001
            log.warning("嵌入模型不可用，退回 BM25: %s", exc)
            return False

    # ── 建索引 ──────────────────────────────────────────
    def _signature(self, keys: list[str]) -> str:
        return f"{len(keys)}:" + ",".join(keys[-8:])

    def build(self, keys: list[str], texts: list[str], rows: list[int] | None = None) -> None:
        """全量或增量编码。rows 指定这些 text 对应的 chunk 下标（稀疏填充），
        其余位置留零向量（余弦=0，不影响排序）。"""
        if not self._ensure_model():
            return
        sig = self._signature(keys)
        if sig == self.sig and self.vecs is not None:
            return
        t0 = time.monotonic()
        n = len(keys)
        dim = self.dim_hint
        emb = np.zeros((n, dim), dtype=np.float32)
        idxs = rows if rows is not None else list(range(len(texts)))
        sub = [texts[j] for j in idxs]
        if sub:
            got = self.model.encode(
                sub, batch_size=64, normalize_embeddings=True,
                show_progress_bar=False, convert_to_numpy=True,
            ).astype(np.float32)
            dim = got.shape[1]
            emb = np.zeros((n, dim), dtype=np.float32)
            emb[np.array(idxs, dtype=np.int64)] = got
        self.vecs = emb
        self.sig = sig
        try:
            np.savez_compressed(CACHE, vecs=emb, keys=np.array(keys, dtype=object))
        except OSError:
            pass
        log.info("向量索引完成：%d/%d 段，%.1fs，dim=%d", len(sub), n, time.monotonic() - t0, dim)

    def load_cache(self, keys: list[str]) -> bool:
        """启动时尝试读缓存；签名一致直接用。"""
        if not CACHE.exists():
            return False
        try:
            with np.load(CACHE, allow_pickle=True) as data:
                cached = [str(k) for k in data["keys"]]
                if self._signature(cached) == self._signature(keys):
                    self.vecs = data["vecs"].astype(np.float32)
                    self.sig = self._signature(keys)
                    log.info("向量缓存命中：%d 段", len(cached))
                    return True
        except Exception as exc:  # noqa: BLE001
            log.debug("向量缓存读取失败: %s", exc)
        return False

    # ── 查询 ────────────────────────────────────────────
    def top(self, question: str, n_chunks: int, k: int = 12) -> list[tuple[int, float]]:
        """返回 [(chunk下标, 余弦相似度)]，模型不可用时返回空。"""
        if self.vecs is None or n_chunks != self.vecs.shape[0]:
            if not self._ensure_model() or self.vecs is None:
                return []
            if n_chunks != self.vecs.shape[0]:
                return []                       # 段数变了但还没重建，本轮纯 BM25
        if self.model is None and not self._ensure_model():
            return []
        try:
            q = self.model.encode([question], normalize_embeddings=True,
                                  convert_to_numpy=True).astype(np.float32)
            sims = (self.vecs @ q.T).ravel()
            idx = np.argpartition(-sims, min(k, len(sims) - 1))[:k]
            return [(int(i), float(sims[i])) for i in idx]
        except Exception as exc:  # noqa: BLE001
            log.debug("向量查询失败: %s", exc)
            return []
