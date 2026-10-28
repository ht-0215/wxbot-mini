"""端到端 FAE 问答评测：真实口吻问题 → 检索+LLM 完整链路，人工检查要点打分。

与 eval_kb（只测检索命中）互补：这里验证最终发给客户的答复质量。
判分：答复包含 check 关键词之一即 OK；打印前 200 字供人工复核。

用法：python eval_e2e.py          # 全部用例
      python eval_e2e.py 3        # 前 3 条
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from bot import config, llm, memory as mem_mod, router
from run import make_kb

CASES = [
    # (问题, 期望包含的关键词列表, 说明)
    ("kd5886 怎么把一个端口设为百兆全双工", ["100", "full", "duplex", "speed"], "端口速率协商"),
    ("VLAN 里 pvid 是干什么的", ["pvid", "PVID", "无 Tag", "untag"], "概念解释"),
    ("镜像烧写时串口波特率设多少", ["115200", "baudrate"], "烧写实操"),
    ("sdk 怎么编译", ["make", "编译"], "SDK 编译"),
    ("怎么做端口流量统计", ["统计", "counter", "stat"], "诊断"),
    ("rgmii 和 gmii 有什么区别", ["rgmii", "gmii", "GMII"], "接口概念"),
    ("端口加入vlan 10 并设为access口", ["pvid", "untagged", "access"], "VLAN 配置实操"),
    ("启动脚本放在哪里", ["start.sh", "/mnt/flash", "flash"], "demo 板实操"),
]


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(CASES)
    cfg = config.load()
    cfg.rate.send_interval = (0, 0)
    kb = make_kb(cfg)
    kb.reload(force=True)
    t_end = time.monotonic() + 90          # 等向量预热，最多 90s
    while time.monotonic() < t_end:
        v = kb._vec
        if v is not None and v.vecs is not None and v.model is not None:
            break
        time.sleep(2)
    mem = mem_mod.SessionMemory(cfg)
    ok = 0
    for q, checks, note in CASES[:limit]:
        question = llm.build_question(cfg, mem, "bot测试群", "客户", q, kb=kb)
        reply = llm.ask(cfg, router.system_prompt_for(cfg, "bot测试群"), question)
        hit = any(c.lower() in reply.lower() for c in checks)
        ok += hit
        print(f"\n== [{'OK' if hit else 'MISS'}] {note} | Q: {q}")
        print(reply[:220].replace("\n", " ¶ "))
    print(f"\nSUMMARY {ok}/{min(limit, len(CASES))}")


if __name__ == "__main__":
    main()
