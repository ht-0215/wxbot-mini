"""分步截图诊断：Alt+E → 点放大镜 → 粘贴，每步存图。"""
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

from PIL import ImageGrab

from bot import emotion
from bot.wechat import WeChat

wx = WeChat()
wx.focus("文件传输助手")
time.sleep(1.0)
assert emotion._activate_main_window()

def shot(tag, rect):
    ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom)).save(f"_step_{tag}.png")
    print("RESULT shot:", tag)

emotion._press(emotion.VK_MENU, 0x45)
assert emotion._wait_popover(True), "面板未开"
time.sleep(0.6)
win = emotion._find(emotion.POPOVER_CLASS)
r = win.BoundingRectangle
shot("1_opened", r)

w, h = r.right - r.left, r.bottom - r.top
emotion._click(r.left + w * emotion.SEARCH_ICON_RATIO[0], r.top + h * emotion.SEARCH_ICON_RATIO[1])
time.sleep(0.8)
win = emotion._find(emotion.POPOVER_CLASS, timeout=1.0) or win
r = win.BoundingRectangle
shot("2_after_search_click", r)

if emotion._set_clipboard("开心"):
    emotion._press(emotion.VK_CONTROL, 0x56)
time.sleep(2.0)
win = emotion._find(emotion.POPOVER_CLASS, timeout=1.0) or win
r = win.BoundingRectangle
shot("3_after_paste", r)
