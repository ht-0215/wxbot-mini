"""防撤回：基于库自带 RecallGuard，撤回的消息留档并可查询回显。

启用：config.features.recall_guard: true（默认关）。
查询：聊天里发 `/撤回` 或 `/撤回 5` 列出最近被撤回的消息。
"""
from __future__ import annotations

import logging

log = logging.getLogger("wxbot.recall")


def make_guard(wx, mirror_dir: str | None = None):
    """从 WeChat 封装对象创建 RecallGuard；库不支持时返回 None。"""
    try:
        from wechatauto import RecallGuard
    except ImportError:
        try:
            from wxauto import RecallGuard
        except ImportError:
            log.info("当前微信库无 RecallGuard，防撤回功能跳过")
            return None
    try:
        guard = RecallGuard(wx.db, mirror_dir=mirror_dir, scan=True)
        log.info("防撤回已启用（mirror=%s）", mirror_dir or "默认")
        return guard
    except Exception as exc:  # noqa: BLE001
        log.warning("RecallGuard 初始化失败: %s", exc)
        return None


def format_recalled(guard, chat: str | None, limit: int = 5) -> str:
    try:
        rows = guard.get_recalled(chat=chat, limit=limit)
    except Exception as exc:  # noqa: BLE001
        return f"撤回记录查询失败: {exc}"
    if not rows:
        return "最近没有被撤回的消息"
    lines = []
    for r in rows[:limit]:
        who = r.get("sender") or r.get("from") or "?"
        txt = (r.get("content") or "").strip()[:120]
        ts = r.get("time") or r.get("ts") or ""
        lines.append(f"- {ts} {who}: {txt}")
    return "被撤回的消息：\n" + "\n".join(lines)
