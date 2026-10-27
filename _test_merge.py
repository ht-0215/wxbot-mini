"""合并窗口逻辑测试：模拟轮询 3 次消息递增，验证只回一次且内容为合并文本。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import logging

logging.basicConfig(level=logging.WARNING)

from bot import config as cfg_mod
from bot import knowledge as kb_mod
from bot import memory as mem_mod
from bot import router
from run import make_kb

cfg = cfg_mod.load()
cfg.rate.merge_window_seconds = 0.6
cfg.rate.poll_seconds = 0.2

texts = ["第一条问题", "第一条问题\n第二条补充", "第一条问题\n第二条补充\n第三条追问"]


class FakeWX:
    def __init__(self):
        self.i = 0
        self.sent = []

    def unread_chats(self):
        return ["叶子"]

    def read_latest(self, chat):
        from bot.wechat import Message
        t = texts[min(self.i, len(texts) - 1)]
        self.i += 1
        return [Message(chat=chat, sender="客户", text=t)]

    def send(self, chat, text):
        self.sent.append(text)


wx = FakeWX()
mem = mem_mod.SessionMemory(cfg)
kb = make_kb(cfg)
kb.reload(force=True)

# 复刻 run.run 的窗口逻辑（不循环阻塞，手动跑 6 拍）
from bot import llm, webpage
last_seen: dict[str, str] = {}
pending: dict[str, tuple[str, str, float]] = {}
from run import handle

t_end = time.monotonic() + 2.0
while time.monotonic() < t_end:
    now = time.monotonic()
    for chat in wx.unread_chats():
        msgs = wx.read_latest(chat)
        text = "\n".join(m.text for m in msgs if m.text)
        if text == last_seen.get(chat):
            continue
        last_seen[chat] = text
        sender = msgs[-1].sender
        prev = pending.get(chat)
        if prev:
            sender = prev[1] or sender
        pending[chat] = (text, sender, now + cfg.rate.merge_window_seconds)
    due = [c for c, (_, _, dl) in pending.items() if dl <= now]
    for chat in due:
        t, s, _ = pending.pop(chat)
        print("== handle once with:", t.replace("\n", " | "))
        handle(cfg, wx, mem, chat, t, s, kb=kb)
    time.sleep(cfg.rate.poll_seconds)

print("RESULT replies:", len(wx.sent))
assert len(wx.sent) == 1, "应只回一次"
print("OK merge window works")
