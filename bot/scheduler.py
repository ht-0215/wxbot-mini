"""定时提醒：解析聊天文本里的时间表达，到期把提醒发回原会话。

支持两种格式：
    相对时间  "15分钟后提醒我拿快递" / "2小时后..." / "30秒后..."
    每日重复  "每天早上八点叫我起床" / "每天 8:30 ..."

Task 存内存列表，daemon 线程每 5s 扫一次，到期调 send(chat, msg)。
重复解析入口 parse_reminder()；注册后回复一句确认由调用方发送。
"""
from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

log = logging.getLogger("wxbot.sched")

CN_NUM = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "半": 30}


@dataclass
class Task:
    chat: str
    note: str           # 提醒内容
    next_at: float      # monotonic 到期时刻
    every: float | None = None    # 每日重复：间隔秒数


@dataclass
class Scheduler:
    send: object = None            # callable(chat, text)
    tasks: list[Task] = field(default_factory=list)
    _stop: bool = False

    def add(self, chat: str, text: str) -> str | None:
        """从文本解析提醒；成功返回确认文案，不匹配返回 None。"""
        parsed = parse_reminder(text)
        if parsed is None:
            return None
        delay, every, note = parsed
        self.tasks.append(Task(chat=chat, note=note,
                               next_at=time.monotonic() + delay, every=every))
        when = f"{int(delay)}秒后" if delay < 90 else f"{int(delay // 60)}分钟后"
        if every:
            hh, mm = _hhmm(text)
            when = f"每天 {hh:02d}:{mm:02d}"
        log.info("定时任务注册: %s %s (%s)", chat, when, note)
        return f"好的，{when}提醒你：{note}"

    def run_forever(self, interval: float = 5.0) -> None:
        while not self._stop:
            self.tick()
            time.sleep(interval)

    def tick(self) -> int:
        now = time.monotonic()
        due = [t for t in self.tasks if t.next_at <= now]
        for t in due:
            try:
                self.send(t.chat, f"⏰ 提醒：{t.note}")
            except Exception as exc:  # noqa: BLE001
                log.warning("提醒发送失败: %s", exc)
            if t.every:
                t.next_at = now + t.every
            else:
                self.tasks.remove(t)
        return len(due)


def _hhmm(text: str) -> tuple[int, int]:
    m = re.search(r"(\d{1,2})[:：点](\d{1,2})?", text)
    if m:
        return int(m.group(1)), int(m.group(2) or 0)
    m = re.search(r"(\d{1,2}|[一二两三四五六七八九十])\s*点", text)
    if m:
        g = m.group(1)
        return (CN_NUM.get(g, 0) if not g.isdigit() else int(g)), 0
    return 8, 0


def parse_reminder(text: str) -> tuple[float, float | None, str] | None:
    """返回 (首次延迟秒, 重复间隔秒或None, 提醒内容)。"""
    text = text.strip()
    if not any(k in text for k in ("提醒", "叫我", "喊我")):
        return None
    m = re.search(r"(\d+|半|[一二两三四五六七八九十])\s*(分钟|分|小时|秒钟?|天)\s*之?后?", text)
    if m:
        g = m.group(1)
        num = float(g) if g.isdigit() else float(CN_NUM.get(g, 0) or 0)
        if not num:
            return None
        unit = m.group(2)
        mult = 3600.0 if unit.startswith("小时") else \
            86400.0 if unit.startswith("天") else \
            60.0 if unit.startswith("分") else 1.0
        if g == "半":
            num = 0.5                       # 半小时/半分钟
        delay = num * mult
        note = text[m.end():].strip().lstrip(":：，, ")
        note = re.sub(r"^(提醒|叫|喊)(我)?[:：,，]?\s*", "", note)
        return delay, None, (note or "时间到")
    if "每天" in text:
        hh, mm = _hhmm(text)
        now = datetime.now()
        target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        delay = (target - now).total_seconds()
        note = re.sub(r"^每天\s*(上午|下午|早上|晚上|凌晨)?\s*"
                      r"[0-9一二两三四五六七八九十点半]+\s*[:：点]?\s*"
                      r"[0-9一二两三四五六七八九十半]*\s*分?\s*", "", text)
        note = re.sub(r"^(提醒|叫|喊)(我)?[:：,，]?\s*", "", note.strip())
        return delay, 86400.0, (note.strip() or "时间到")
    return None
