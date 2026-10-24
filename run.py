"""wxbot-mini：微信 → 大模型自动回复。

用法：
    python run.py            # 正式运行（需 PC 微信已登录）
    python run.py --check    # 只做配置与依赖自检，不碰微信
"""
from __future__ import annotations

import argparse
import logging
import random
import time

from bot import config as cfg_mod
from bot import llm, router

log = logging.getLogger("wxbot")


def check(cfg) -> None:
    print(f"engine     : {cfg.engine}")
    print(f"base_url   : {cfg.api.base_url}")
    print(f"model      : {cfg.api.model}")
    print(f"api_key    : {'已设置' if cfg.api.api_key else '未设置(' + cfg.api.api_key_env + ')'}")
    print(f"prompts    : default={'有' if 'default' in cfg.prompts else '无'}, routes={len(cfg.routes)} 条")
    print(f"listen     : {cfg.listen or '全部会话'}")
    if cfg.engine == "api":
        reply = llm.ask(cfg, [], "回复“ok”两个字母即可")
        print(f"模型连通性 : {reply[:60]}")


def run(cfg) -> None:
    from bot.wechat import WeChat  # 延迟导入：--check 不需要 wxauto

    wx = WeChat()
    last_seen: dict[str, str] = {}
    log.info("进入轮询循环，Ctrl+C 退出")
    while True:
        for chat in wx.unread_chats():
            if not router.should_listen(cfg, chat):
                continue
            msgs = wx.read_latest(chat)
            if not msgs:
                continue
            text = "\n".join(m.text for m in msgs if m.text)
            if text == last_seen.get(chat):
                continue  # 已回过，去重
            last_seen[chat] = text

            reply = llm.ask(cfg, [], text)
            lo, hi = cfg.rate.send_interval
            time.sleep(random.uniform(lo, hi))
            wx.send(chat, reply)
        time.sleep(cfg.rate.merge_window_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="wxbot-mini")
    parser.add_argument("--check", action="store_true", help="只做配置与连通性自检")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    cfg = cfg_mod.load()
    if args.check:
        check(cfg)
        return
    try:
        run(cfg)
    except KeyboardInterrupt:
        print("bye")


if __name__ == "__main__":
    main()
