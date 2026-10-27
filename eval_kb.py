"""知识库离线评测：典型 FAE 问题 → 期望命中的关键词。

用法：python eval_kb.py           # 跑全部用例
      python eval_kb.py -v        # 打印每条 top-k

判定：expected 中任一子串出现在 top_k 结果的 source/title/body 即算命中。
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from bot import config
from bot.knowledge import _tokens_of
from run import make_kb

CASES = [
    # (问题, [期望关键词，任一命中即可], 说明)
    ("kd5860 的 dts 里 rgmii 怎么配置", ["kd5860", "rgmii"], "dts 查询"),
    ("kd5886 SPI-NOR 启动选哪个 u-boot", ["sf", "u-boot"], "固件选型"),
    ("rgmii 吞吐减半查什么", ["delay", "RXCLK"], "rgmii 排错"),
    ("link 起不来先查什么", ["GTXCLK"], "rgmii 排错2"),
    ("jffs2 镜像怎么制作", ["jffs2", "mkfs"], "fs 制作"),
    ("ram 文件系统 rootfs.cpio 怎么做", ["cpio", "ram"], "ramfs 制作"),
    ("ext4 rootfs 制作步骤", ["ext4", "mkfs"], "ext4 制作"),
    ("GS8611 PHY 驱动入口", ["gs8611", "phy"], "PHY 驱动"),
    ("phy_nocxn 是什么", ["phynull", "phy_nocxn"], "标识符直查"),
    ("以太网发包测试工具", ["pie_tx", "发包"], "工具"),
    ("DDR 主频怎么确认", ["1600", "UBOOT"], "boot readme"),
    ("L2 组播 API", ["组播", "multicast"], "API 文档"),
    ("QoS 优先级映射", ["优先级", "QoS"], "核心功能"),
    ("内核怎么编译 bzImage", ["make", "bzImage"], "编译"),
    ("SPI 配置开发指南", ["spi"], "SPI 指南"),
]


def main() -> None:
    verbose = "-v" in sys.argv
    cfg = config.load()
    kb = make_kb(cfg)
    t0 = time.perf_counter()
    kb.reload(force=True)
    print(f"load {time.perf_counter()-t0:.1f}s  chunks={len(kb._chunks)}")
    ok = 0
    t0 = time.perf_counter()
    for q, expects, note in CASES:
        hits = kb.search(q)
        joined = " ".join((c.source + " " + c.title + " " + c.body).lower() for c in hits)
        hit = any(e.lower() in joined for e in expects)
        ok += hit
        mark = "✓" if hit else "✗"
        print(f"{mark} [{note}] {q}")
        if verbose or not hit:
            for c in hits:
                print(f"    → {c.source[:70]} | {c.title[:36]}")
    dt = time.perf_counter() - t0
    print(f"\n{ok}/{len(CASES)} hit, {dt*1000/len(CASES):.0f}ms/query avg")


if __name__ == "__main__":
    main()
