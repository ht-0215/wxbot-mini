"""微信封装：兼容 wxauto / wechatauto-replica 两种后端。

暴露五个动作：取未读会话、切前台、读某会话最新消息、发文本、发图片。
wechatauto-replica 的导入名是 wechatauto，模块名与属性名略有差异，
本文件统一成 Message(dataclass) 输出给上层。
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


def _import_backend():
    try:
        from wxauto import WeChat as _WeChat  # noqa: PLC0415
        return _WeChat, "wxauto"
    except ImportError:
        pass
    try:
        from wechatauto import WeChat as _WeChat  # noqa: PLC0415
        return _WeChat, "wechatauto"
    except ImportError as exc:
        raise RuntimeError(
            "未安装微信自动化库。pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "
            "wechatauto-replica（或 wxauto），并保持 PC 微信已登录、最小化到托盘。"
        ) from exc


class WeChat:
    def __init__(self) -> None:
        cls, self.backend = _import_backend()
        self._wx = cls()
        log.info("已连接微信客户端（后端: %s）", self.backend)

    def unread_chats(self) -> list[str]:
        """未读会话名单：GetSession 列表里 unread>0 的行。"""
        try:
            sessions = self._wx.GetSession()
            return [s.name for s in sessions if getattr(s, "unread", 0)]
        except Exception as exc:  # noqa: BLE001
            log.warning("获取会话列表失败: %s", exc)
            return []

    def focus(self, chat: str) -> None:
        """把会话切到前台，让表情面板快捷键落在它身上。"""
        try:
            self._wx.ChatWith(chat)
        except Exception as exc:  # noqa: BLE001
            log.warning("切换会话 %s 失败: %s", chat, exc)

    def read_latest(self, chat: str) -> list[Message]:
        """DB-only：读会话列表 summary（解密本地库，不占前台）。"""
        try:
            for s in self._wx.GetSession():
                if s.name != chat:
                    continue
                summary = str(getattr(s, "summary", "") or "").strip()
                if summary:
                    sender, _, rest = summary.partition(":")
                    # 群列表常是 "昵称:消息"；单人会话无冒号则整体当正文
                    if rest.strip():
                        return [Message(chat=chat, sender=sender.strip(), text=rest.strip())]
                    return [Message(chat=chat, sender="", text=summary)]
        except Exception as exc:  # noqa: BLE001
            log.warning("读取会话 %s 失败: %s", chat, exc)
        return []

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
