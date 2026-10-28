"""一步一进程的双账号对话：每步单独 python 进程，避免同进程双 GUI 共读同一 DB。

  python demo_chat.py send  "问题"     # 叶子窗口发问（标题 Weixin）
  python demo_chat.py reply            # 本人窗口读最新问、生成并回复（标题 微信）
"""
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("demo")
sys.stdout.reconfigure(encoding="utf-8")

import uiautomation as auto
from wechatauto import WeChat
from wechatauto.guia import WeChatGUI

FAE_TITLE, CLIENT_TITLE = "微信", "Weixin"
CLIENT_CHAT, FAE_CHAT = "H", "叶子"


def all_windows() -> list[tuple[int, object]]:
    out = []
    for w in auto.GetRootControl().GetChildren():
        if (w.ClassName or "") == "mmui::MainWindow":
            out.append((w.NativeWindowHandle, w))
    return out


def pick_window(title: str, role: str) -> int:
    """标题都是'微信'时不可靠：role=fae 取含「叶子」会话的一端，client 取另一端。"""
    wins = all_windows()
    if len(wins) < 2:                       # 单窗口时谁都是
        return wins[0][0] if wins else 0
    for h, w in wins:                       # 先按标题精确匹配
        if w.Name == title:
            return h
    # 标题撞名：按 rect 稳定排序，左边的当 FAE（本人），右边的当客户端
    ordered = sorted(wins, key=lambda t: t[1].BoundingRectangle.left)
    return ordered[0][0] if role == "fae" else ordered[1][0]


def do_send(question: str) -> None:
    wx = WeChat(gui=WeChatGUI(hwnd=pick_window(CLIENT_TITLE, "client")))
    wx.ChatWith(CLIENT_CHAT)
    time.sleep(1.0)
    wx.SendMsg(msg=question, who=CLIENT_CHAT)
    log.info("[客户·叶子→H] %s", question)


def do_reply() -> None:
    from bot import config as cfg_mod
    from bot import llm, memory as mem_mod, router
    from run import make_kb

    cfg = cfg_mod.load()
    wx = WeChat(gui=WeChatGUI(hwnd=pick_window(FAE_TITLE, "fae")))
    texts = []
    for s in wx.GetSession():
        if s.name == FAE_CHAT:
            t = str(getattr(s, "summary", "") or "").strip()
            if t:
                texts = [t]
            break
    if not texts:
        # UI 兜底
        wx.ChatWith(FAE_CHAT)
        time.sleep(1.0)
        for m in wx.GetAllMessage()[-5:]:
            if getattr(m, "type", "") == "text" and str(getattr(m, "attr", "")) == "friend":
                c = str(getattr(m, "content", "")).strip()
                if c:
                    texts.append(c)
    if not texts:
        log.warning("本人端没读到新消息")
        return
    text = "\n".join(texts)
    log.info("[读到] %s", text)

    kb = make_kb(cfg)
    kb.reload(force=True)
    mem = mem_mod.SessionMemory(cfg)
    question = llm.build_question(cfg, mem, FAE_CHAT, "客户", text, kb=kb)
    reply = llm.ask(cfg, router.system_prompt_for(cfg, FAE_CHAT), question)
    mem.append(FAE_CHAT, "客户", text)

    wx.ChatWith(FAE_CHAT)
    time.sleep(1.0)
    wx.SendMsg(msg=reply, who=FAE_CHAT)
    log.info("[FAE·H→叶子] %s", reply[:150])


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "send"
    if mode == "send":
        do_send(sys.argv[2] if len(sys.argv) > 2 else "kd5886 用 SPI-NOR 启动，u-boot 该选哪个？")
    else:
        do_reply()
