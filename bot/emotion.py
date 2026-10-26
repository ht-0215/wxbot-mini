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
VK_DOWN = 0x28
KEYEVENTF_KEYUP = 0x0002
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002

# 面板内元素比例坐标（来自实测截图，见 _panel.png）：
#   左下放大镜(搜索) ≈ (0.109, 0.902)；搜索后结果第一格 ≈ (0.109, 0.182)
SEARCH_ICON_RATIO = (0.109, 0.902)
FIRST_RESULT_RATIO = (0.109, 0.182)

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


# ── panel 模式：键盘 + 坐标点击 ─────────────────────────
def _press(*vks: int) -> None:
    for vk in vks:
        _user32.keybd_event(vk, 0, 0, 0)
    for vk in reversed(vks):
        _user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def _click(x: int, y: int) -> None:
    _user32.SetCursorPos(int(x), int(y))
    _user32.mouse_event(0x0002, 0, 0, MK_LBUTTON, 0)   # down
    _user32.mouse_event(0x0800, 0, 0, MK_LBUTTON, 0)   # up


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


MAIN_CLASS = "mmui::MainWindow"
POPOVER_CLASS = "mmui::EmoticonPopover"


def _find(class_name: str, timeout: float = 2.0):
    """按窗口类名找顶层窗口（实测 GetRootControl 子级可见；FindWindow 不可靠）。"""
    import uiautomation as auto  # noqa: PLC0415
    end = time.monotonic() + timeout
    while True:
        for w in auto.GetRootControl().GetChildren():
            if (w.ClassName or "") == class_name:
                return w
        if time.monotonic() >= end:
            return None
        time.sleep(0.2)


def _popover_alive() -> bool:
    win = _find(POPOVER_CLASS, timeout=0.5)
    return bool(win)


def _wait_popover(open_state: bool, timeout: float = 3.0) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if _popover_alive() == open_state:
            return True
        time.sleep(0.15)
    return False


def _activate_main_window() -> bool:
    """把微信主窗口置于前台——Alt+E 只发给前台焦点窗口。"""
    win = _find(MAIN_CLASS)
    if not win:
        return False
    try:
        win.SetActive()
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.5)
    return True


def send_from_panel(keyword: str, search_wait: float = 2.0) -> bool:
    """按真实手动顺序发搜索表情，并把首个结果缓存到 emojis/<关键词>/：

    激活主窗口 → Alt+E 开面板 → 点左下放大镜进搜索视图 →
    Ctrl+V 粘关键词 → 等结果渲染 → 截图裁首个结果存缓存 →
    点第一格发送 → 面板自动关闭作为成功依据。

    缓存后同关键词下次直接走 pick_image 秒发，不再碰 UI。
    """
    try:
        if not _activate_main_window():
            log.warning("未能激活微信主窗口，跳过表情")
            return False
        _press(VK_MENU, 0x45)
        if not _wait_popover(True):
            log.warning("表情面板未能打开")
            return False
        time.sleep(0.5)
        win = _find(POPOVER_CLASS)
        if win is None:
            return False
        r = win.BoundingRectangle
        w, h = r.right - r.left, r.bottom - r.top

        # ① 点左下放大镜，进入搜索视图
        _click(r.left + w * SEARCH_ICON_RATIO[0], r.top + h * SEARCH_ICON_RATIO[1])
        time.sleep(0.6)

        # ② 粘贴关键词，等搜索结果渲染
        if keyword and _set_clipboard(keyword):
            _press(VK_CONTROL, 0x56)
        time.sleep(search_wait)

        # ③ 截图裁第一个结果，落缓存（失败不影响发送）
        _cache_first_result(r, keyword)

        # ④ 点第一格发送，面板关闭即成功
        _click(r.left + w * FIRST_RESULT_RATIO[0], r.top + h * FIRST_RESULT_RATIO[1])
        closed = _wait_popover(False, timeout=2.5)
        log.info("表情面板: %s（%s）", keyword, "发送成功" if closed else "面板未关，未确认")
        return closed
    except Exception as exc:  # noqa: BLE001
        log.warning("表情面板发送失败: %s", exc)
        return False


def _cache_first_result(rect, keyword: str = "") -> None:
    """截取面板搜索结果第一格，存为 emojis/<关键词>/first.png。"""
    try:
        from PIL import ImageGrab  # noqa: PLC0415
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        cell = (
            int(rect.left + w * 0.05), int(rect.top + h * 0.15),
            int(rect.left + w * 0.22), int(rect.top + h * 0.34),
        )
        img = ImageGrab.grab(bbox=cell)
        out_dir = ROOT / "emojis" / (keyword or "misc")
        out_dir.mkdir(parents=True, exist_ok=True)
        img.save(out_dir / "first.png")
        log.info("表情已缓存: %s", out_dir / "first.png")
    except Exception as exc:  # noqa: BLE001
        log.debug("缓存表情截图失败: %s", exc)
