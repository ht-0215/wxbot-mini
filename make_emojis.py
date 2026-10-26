"""从表情面板截图 _panel.png 裁出常用表情，生成 emojis/<关键词>/first.png。

用法：python make_emojis.py
前置：先跑一次面板流程（或手动截图）把面板整窗存为 _panel.png。
坐标基于 1028x1028 面板截图，按行/列比例换算，窗口缩放后重截图即可重建。
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_panel.png"
CELL = 46  # 半径像素，略大于图标留白

# (x, y, 关键词)：x/y 为图标中心，取自 _panel.png 网格
ICONS = [
    # 第一行：最近使用
    (105, 192, "收到"),      # OK 手势
    (190, 192, "无语"),      # 捂脸
    (277, 192, "哈哈"),      # 吃瓜笑
    (364, 192, "嗯"),        # 抿嘴
    (450, 192, "这个"),      # 指人
    (537, 192, "握手"),      # 握手
    (624, 192, "思考"),      # 托腮
    (797, 192, "狗头"),      # 小狗
    # 第二行：所有表情首行
    (105, 348, "微笑"),
    (364, 434, "开心"),      # 第二行第四列：咧嘴大笑
    (277, 348, "喜欢"),      # 心心眼
    (364, 348, "惊"),        # 惊讶
    (450, 348, "酷"),        # 墨镜
    (537, 348, "哭"),        # 大哭
    (624, 348, "困"),        # 闭眼睡
    (884, 348, "委屈"),      # 撇嘴
]


def main() -> None:
    img = Image.open(SRC).convert("RGBA")
    lib = ROOT / "stickers"
    lib.mkdir(parents=True, exist_ok=True)
    for x, y, kw in ICONS:
        box = (x - CELL, y - CELL, x + CELL, y + CELL)
        out = lib / f"{kw}.png"
        img.crop(box).save(out)
        print(f"stickers/{kw}.png  <- {box}")
    print(f"done: {len(ICONS)} stickers")


if __name__ == "__main__":
    main()
