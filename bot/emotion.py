"""情绪表情包：解析回复末尾的 [happy] 标签，映射到 emojis/<情绪>/ 里的图片。

用法：模型在回复末尾打 [happy]，发送时先发文本、再随机发一张该情绪的图片。
目录约定：项目根 emojis/happy/*.png|jpg|gif，缺目录时静默跳过配图。
"""
from __future__ import annotations

import logging
import random
import re
from pathlib import Path

log = logging.getLogger("wxbot.emoji")

TAG_RE = re.compile(r"\[([a-zA-Z_\- ]{1,20})\]\s*$")
IMG_EXTS = (".png", ".jpg", ".jpeg", ".gif")

ROOT = Path(__file__).resolve().parent.parent


def split_reply(text: str) -> tuple[str, str | None]:
    """拆出正文与情绪标签。'[happy]' 之类只在行尾生效。"""
    m = TAG_RE.search(text.strip())
    if not m:
        return text.strip(), None
    return text[: m.start()].strip(), m.group(1).strip().lower() or None


def pick_image(emotion: str) -> Path | None:
    d = ROOT / "emojis" / emotion
    if not d.is_dir():
        return None
    images = [p for p in d.iterdir() if p.suffix.lower() in IMG_EXTS]
    return random.choice(images) if images else None
