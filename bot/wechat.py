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
    def __init__(self, hwnd: int | None = None, title: str | None = None) -> None:
        """hwnd/title 可选：双开时把 UI 操作固定到指定窗口。

        不传则沿用库默认（跟随激活窗口）。GetSession 走共享 DB 不受影响；
        SendMsg/ChatWith 等 UI 动作会绑定所选窗口。
        """
        cls, self.backend = _import_backend()
        gui = None
        if hwnd or title:
            try:
                gui_mod = (__import__("wxauto.guia", fromlist=["WeChatGUI"])
                           if self.backend == "wxauto"
                           else __import__("wechatauto.guia", fromlist=["WeChatGUI"]))
                gui = gui_mod.WeChatGUI(title=title or "微信", hwnd=hwnd)
            except Exception as exc:  # noqa: BLE001
                log.warning("窗口绑定失败(%s)，回落默认: %s", (title or hwnd), exc)
        self._wx = None
        if gui is not None:
            try:
                self._wx = cls(gui=gui)
            except Exception as exc:  # noqa: BLE001
                log.debug("gui 参数不被支持: %s", exc)
        if self._wx is None:
            self._wx = cls()
        log.info("已连接微信客户端（后端: %s，窗口: %s）",
                 self.backend, hwnd or title or "默认")

    @property
    def db(self):
        """底层 WeChatDB，供 RecallGuard 等复用。"""
        return getattr(self._wx, "_db", None)

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
