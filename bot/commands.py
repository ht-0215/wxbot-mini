"""本地指令：以 / 开头的短命令直接执行，不送模型。

在 handle() 入口处调用 dispatch()；返回 True 表示已处理（调用方跳过 LLM）。

指令表：
    /状态                    回复统计：今日问答数、知识库段数、监听名单
    /清空记忆 <会话名>        删除指定会话记忆文件
    /帮助                    列出全部指令
未知 /xxx：回一行提示，不调模型。
"""
from __future__ import annotations

import logging

log = logging.getLogger("wxbot.cmd")

HELP_LINES = [
    "/状态 — 今日问答统计与知识库概况",
    "/清空记忆 <会话名> — 删除该会话记忆",
    "/帮助 — 指令列表",
]


def dispatch(cfg, mem, kb, chat: str, text: str) -> str | None:
    """text 以 / 开头则本地处理，返回要发送的文本；否则返回 None 交给模型。"""
    text = text.strip()
    if not text.startswith("/"):
        return None
    parts = text.split(maxsplit=2)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    if cmd in ("/帮助", "/help"):
        reply = "\n".join(HELP_LINES)
    elif cmd in ("/状态", "/status"):
        lines = [f"监听: {', '.join(cfg.listen) or '全部'}"]
        if kb is not None:
            lines.append(f"知识库: {len(kb._chunks)} 段")
        _, recent = mem.load(chat)
        lines.append(f"本会话记忆: {len(recent)} 条")
        reply = "\n".join(lines)
    elif cmd in ("/清空记忆", "/clear") and arg:
        mem.clear(arg)
        reply = f"已清空会话[{arg}]的记忆"
    else:
        reply = f"未知指令 {cmd}，输入 /帮助 查看列表"
    log.info("指令 %s (%s)", cmd, chat)
    return reply
