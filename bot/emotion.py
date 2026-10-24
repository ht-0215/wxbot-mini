"""表情包：优先用微信自带表情面板（Alt+E + 关键词搜索），本地目录兜底。

两种模式（config: features.emotion_mode）：
    panel  : 回复带 [加油] 之类标签时，Alt+E 打开表情面板 → 搜索框粘贴关键词
             → 回车选中第一个结果发出。用的是微信内置表情库，无需自备图片。
    folder : 从 emojis/<标签>/*.png 随机挑一张，走 SendFiles 发送。

panel 模式实现：Alt+E / Ctrl+V / Enter 通过 ctypes 直接发按键事件，
剪贴板借 PowerShell Set-Clipboard 写入中文（keybd 无法直接输入中文）。
前提：调用前 wxauto 已 ChatWith 把目标会话切到前台，输入框有焦点。
"""
from __future__ import annotations

import ctypes
import logging
import random
import re
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

log = logging.getLogger("wxbot.emoji")

# 行尾标签，允许中文关键词：[加油] [nice] [狗头]
TAG_RE = re.compile(r"\[([^\[\]\n]{1,12})\]\s*$")
IMG_EXTS = (".png", ".jpg", ".jpeg", ".gif")

ROOT = Path(__file__).resolve().parent.parent

VK_CONTROL = 0x11
VK_MENU = 0x12
VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002

_user32 = ctypes.windll.user32


def split_reply(text: str) -> tuple[str, str | None]:
    """拆出正文与情绪标签。'[加油]' 之类只在末尾生效。"""
    stripped = text.strip()
    m = TAG_RE.search(stripped)
    if not m:
        return stripped, None
    return stripped[: m.start()].strip(), m.group(1).strip() or None


def pick_image(emotion: str) -> Path | None:
    """folder 模式：emojis/<情绪>/ 下随机取一张图。"""
    d = ROOT / "emojis" / emotion
    if not d.is_dir():
        return None
    images = [p for p in d.iterdir() if p.suffix.lower() in IMG_EXTS]
    return random.choice(images) if images else None


# ── panel 模式：键盘事件 ────────────────────────────────
def _press(*vks: int) -> None:
    for vk in vks:
        _user32.keybd_event(vk, 0, 0, 0)
    for vk in reversed(vks):
        _user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def _set_clipboard(text: str) -> bool:
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{text}'"],
            capture_output=True, timeout=10, check=False,
        )
        return True
    except Exception as exc:  # noqa: BLE001
        log.debug("写剪贴板失败: %s", exc)
        return False


def send_from_panel(keyword: str, search_wait: float = 1.2) -> bool:
    """Alt+E 打开表情面板 → 粘贴关键词搜索 → 回车发第一个结果。

    返回是否走完流程（不代表对方一定收到，微信在前台时才有意义）。
    """
    try:
        _press(VK_MENU, 0x45)          # Alt+E 打开表情面板
        time.sleep(0.4)
        if keyword and _set_clipboard(keyword):
            _press(VK_CONTROL, 0x56)   # Ctrl+V 把关键词粘进搜索框
            time.sleep(search_wait)    # 等搜索结果渲染
        _press(VK_RETURN)              # 回车选中第一个结果并发送
        log.info("表情面板: %s", keyword)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("表情面板发送失败: %s", exc)
        return False
