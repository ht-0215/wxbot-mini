"""链接读取：抓取消息里的 http(s) 链接正文，截断后拼进提问。"""
from __future__ import annotations

import logging
import re
from html.parser import HTMLParser

import urllib.request

log = logging.getLogger("wxbot.web")

LINK_RE = re.compile(r"https?://[^\s\u4e00-\u9fff]+")
MAX_CHARS = 1500


class _TextGrab(HTMLParser):
    """粗提取：<script>/<style> 之外的可见文本。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def extract_links(text: str) -> list[str]:
    return LINK_RE.findall(text)[:3]


def fetch_summary(url: str, timeout: int = 10) -> str:
    """返回网页正文纯文本（截断）；失败返回空串，调用方自行忽略。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "wxbot-mini/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(400_000).decode(resp.headers.get_content_charset() or "utf-8", "replace")
        parser = _TextGrab()
        parser.feed(raw)
        body = " ".join(parser.parts)
        return re.sub(r"\s+", " ", body)[:MAX_CHARS]
    except Exception as exc:  # noqa: BLE001
        log.debug("抓链接失败 %s: %s", url, exc)
        return ""


def enrich(cfg, text: str) -> str:
    """开启 read_links 时，把消息里链接的正文摘要附加到原文后。"""
    if not getattr(cfg.features, "read_links", True):
        return text
    blocks = []
    for url in extract_links(text):
        body = fetch_summary(url)
        if body:
            blocks.append(f"[链接 {url} 内容] {body}")
    if not blocks:
        return text
    return text + "\n" + "\n".join(blocks)
