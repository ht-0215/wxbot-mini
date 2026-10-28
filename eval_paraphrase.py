"""同义改写句评测：考察语义路相对纯词面 BM25 的增益。

每例：改写问题 + 期望命中的关键词（与 eval_kb 的原句用例互补）。
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from bot import config
from run import make_kb

CASES = [
    ("网口协商出来只有一半速率", ["delay", "RXCLK", "采样", "auto_negotiate", "自协商", "速率"], "吞吐减半的口语说法"),
    ("怎么把某个口划到100这个vlan里", ["pvid", "untagged", "VLAN"], "VLAN 端口配置改写"),
    ("nor flash 上怎么启动", ["sf", "u-boot", "flash", "启动"], "SPI-NOR 选型改写"),
    ("无盘启动用什么文件系统", ["ramfs", "cpio", "rootfs"], "ramfs 改写"),
    ("小系统烧写命令有吗", ["mtd", "flash", "写入", "烧写", "u-boot"], "烧写说法改写"),
]


def run(hybrid: bool) -> tuple[int, float]:
    cfg = config.load()
    cfg.knowledge.hybrid = hybrid
    kb = make_kb(cfg)
    kb.hybrid = hybrid
    kb.reload(force=True)
    if hybrid:
        # 等向量缓存 + 模型预热就绪（最多 90s），否则测的是纯 BM25
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            v = kb._vec
            if v is not None and v.vecs is not None and v.model is not None:
                break
            time.sleep(2)
        print(f"RESULT vec ready: {v is not None and v.model is not None}")
    ok = 0
    t0 = time.perf_counter()
    for q, expects, _ in CASES:
        hits = kb.search(q, top_k=3)
        joined = " ".join((c.source + " " + c.title + " " + c.body).lower() for c in hits)
        if any(e.lower() in joined for e in expects):
            ok += 1
    return ok, time.perf_counter() - t0


if __name__ == "__main__":
    for mode, flag in (("bm25-only", False), ("hybrid", True)):
        ok, dt = run(flag)
        print(f"RESULT {mode}: {ok}/{len(CASES)} hit, {dt:.1f}s")
