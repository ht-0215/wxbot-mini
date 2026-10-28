"""会话记忆：每个会话一个 md 文件，最近 N 条进上下文，超出后摘要压缩。

文件格式（memory/<safe_name>.md）：
    # <chat>
    ## 摘要
    （模型压缩后的长程记忆）
    ## 最近
    - 2026-10-24 15:00 小明: 消息文本
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

from .config import Config

log = logging.getLogger("wxbot.memory")


def _safe_name(chat: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", chat)[:60] or "default"


class SessionMemory:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.root = Path(cfg.memory.dir)
        if not self.root.is_absolute():
            self.root = Path(__file__).resolve().parent.parent / self.root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, chat: str) -> Path:
        return self.root / f"{_safe_name(chat)}.md"

    # ── 读取 ────────────────────────────────────────────
    def load(self, chat: str) -> tuple[str, list[str]]:
        """返回 (摘要文本, 最近消息行列表)。"""
        p = self._path(chat)
        if not p.exists():
            return "", []
        text = p.read_text(encoding="utf-8")
        summary = ""
        recent: list[str] = []
        section = None
        for line in text.splitlines():
            if line.startswith("## 摘要"):
                section = "s"
                continue
            if line.startswith("## 最近"):
                section = "r"
                continue
            if line.startswith("# "):
                continue
            if section == "s" and line.strip():
                summary += line.strip() + "\n"
            elif section == "r" and line.startswith("- "):
                recent.append(line[2:].strip())
        return summary.strip(), recent

    # ── 写入 ────────────────────────────────────────────
    def append(self, chat: str, sender: str, text: str) -> None:
        if not self.cfg.memory.enabled:
            return
        summary, recent = self.load(chat)
        stamp = datetime.now().strftime("%m-%d %H:%M")
        recent.append(f"{stamp} {sender}: {text}" if sender else f"{stamp} {text}")
        self._write(chat, summary, recent[-self.cfg.memory.summarize_after:])

    def rewrite(self, chat: str, summary: str, recent: list[str]) -> None:
        self._write(chat, summary, recent)

    def clear(self, chat: str) -> None:
        p = self._path(chat)
        if p.exists():
            p.unlink()
            log.info("已清空会话记忆: %s", chat)

    def _write(self, chat: str, summary: str, recent: list[str]) -> None:
        lines = [f"# {chat}", "", "## 摘要", summary or "（暂无）", "", "## 最近"]
        lines += [f"- {r}" for r in recent]
        self._path(chat).write_text("\n".join(lines) + "\n", encoding="utf-8")
        log.debug("记忆已写入 %s（最近 %d 条）", chat, len(recent))

    # ── 供 prompt 拼接的上下文块 ─────────────────────────
    def context_block(self, chat: str) -> str:
        summary, recent = self.load(chat)
        if not self.cfg.memory.enabled:
            return ""
        parts = []
        if summary and summary != "（暂无）":
            parts.append(f"【与该对象的历史摘要】{summary}")
        if recent:
            tail = recent[-self.cfg.memory.max_history:]
            parts.append("【最近对话】\n" + "\n".join(tail))
        return "\n".join(parts)

    # ── 超量后触发摘要压缩 ───────────────────────────────
    def needs_summarize(self, chat: str) -> bool:
        _, recent = self.load(chat)
        return len(recent) > self.cfg.memory.summarize_after
