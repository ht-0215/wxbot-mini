"""把 D:\\GitHub\\kd5886\\kd5886 的 docx 官方文档批量转成 markdown 归档进知识库。

用法：python doc2md.py [源目录] [输出目录]
默认：源 D:\\GitHub\\kd5886\\kd5886 → 输出 knowledge/common/kd5886/

转换规则：
  Heading N → #*N；正文段落照抄；表格转 markdown 表格；跳过页眉页脚样式。
  pptx/xlsx 暂不处理（体积大、非检索主力）。
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\GitHub\kd5886\kd5886")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent / "knowledge" / "common" / "kd5886"


def heading_level(p: Paragraph) -> int:
    style = (p.style.name or "") if p.style is not None else ""
    if style.startswith("Heading"):
        try:
            return max(1, min(4, int(style.split()[-1])))
        except (ValueError, IndexError):
            return 1
    if style == "Title":
        return 1
    return 0


def table_md(t: Table) -> str:
    rows = []
    for r in t.rows:
        cells = [" ".join(p.text.split()) for p in r.cells]
        rows.append("| " + " | ".join(cells) + " |")
    if not rows:
        return ""
    ncol = rows[0].count("|") - 1
    rows.insert(1, "|" + " --- |" * ncol)
    return "\n".join(rows)


def iter_blocks(doc):
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            yield Paragraph(child, doc)
        elif tag == "tbl":
            yield Table(child, doc)


def convert(src: Path, dst: Path) -> int:
    doc = Document(str(src))
    lines: list[str] = [f"# {src.stem}", ""]
    count = 0
    for block in iter_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            lvl = heading_level(block)
            lines.append(("#" * lvl + " " + text) if lvl else text)
            lines.append("")
            count += 1
        elif isinstance(block, Table):
            md = table_md(block)
            if md:
                lines += [md, ""]
                count += 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines), encoding="utf-8")
    return count


def main() -> None:
    total = skipped = 0
    for src in sorted(SRC.rglob("*.docx")):
        rel = src.relative_to(SRC)
        dst = OUT / rel.with_suffix(".md")
        try:
            n = convert(src, dst)
            print(f"OK   {rel} -> {dst.relative_to(OUT.parent)} ({n} blocks)")
            total += 1
        except Exception as exc:  # noqa: BLE001
            print(f"SKIP {rel}: {exc}")
            skipped += 1
    print(f"done: {total} converted, {skipped} skipped -> {OUT}")


if __name__ == "__main__":
    main()
