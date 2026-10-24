"""微信封装：优先 wxauto，导入失败时给出明确提示。

暴露四个动作：取未读会话、读某会话最新消息、发文本、发图片。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("wxbot.wechat")


@dataclass
class Message:
    chat: str      # 昵称或群名
    sender: str    # 发送者昵称（群聊时有效）
    text: str


class WeChat:
    def __init__(self) -> None:
        try:
            from wxauto import WeChat as _WeChat  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(
                "未安装 wxauto。pip install wxauto（或 wechatauto-replica），"
                "并保持 PC 微信已登录、最小化到托盘。"
            ) from exc
        self._wx = _WeChat()
        log.info("已连接微信客户端")

    def unread_chats(self) -> list[str]:
        try:
            return [c.name for c in self._wx.GetNextNewMessage(all=True)]
        except Exception as exc:  # noqa: BLE001
            log.warning("获取未读会话失败: %s", exc)
            return []

    def read_latest(self, chat: str) -> list[Message]:
        """切到指定会话并读取最新几条文本消息。"""
        msgs: list[Message] = []
        try:
            self._wx.ChatWith(chat)
            for m in self._wx.GetAllMessage()[-5:]:
                if getattr(m, "type", "") != "text":
                    continue
                msgs.append(Message(chat=chat, sender=str(m.attr), text=str(m.content).strip()))
        except Exception as exc:  # noqa: BLE001
            log.warning("读取会话 %s 失败: %s", chat, exc)
        return [m for m in msgs if m.text]

    def send(self, chat: str, text: str) -> None:
        try:
            self._wx.SendMsg(msg=text, who=chat)
            log.info("→ %s: %s", chat, text[:50])
        except Exception as exc:  # noqa: BLE001
            log.warning("发送到 %s 失败: %s", chat, exc)

    def send_image(self, chat: str, path: Path) -> None:
        try:
            self._wx.SendFiles(filepath=str(path), who=chat)
            log.info("→ %s: [图片 %s]", chat, path.name)
        except Exception as exc:  # noqa: BLE001
            log.warning("发图片到 %s 失败: %s", chat, exc)
