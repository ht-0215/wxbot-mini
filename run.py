"""wxbot-mini：微信 → 大模型自动回复。

用法：
    python run.py            # 轮询模式：接管 PC 微信客户端（需微信已登录）
    python run.py --serve    # HTTP 服务：企业微信智能机器人回调（推荐）
    python run.py --check    # 只做配置与依赖自检，不碰微信
"""
from __future__ import annotations

import argparse
import json
import logging
import logging.handlers
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bot import config as cfg_mod
from bot import emotion, knowledge as kb_mod, llm, memory as mem_mod, router, webpage

log = logging.getLogger("wxbot")


def make_kb(cfg) -> kb_mod.KnowledgeBase:
    dirs = [kb_mod.ROOT / cfg.knowledge.dir] + [Path(x) for x in cfg.knowledge.extra_dirs]
    code_dirs = [Path(x) for x in cfg.knowledge.code_dirs]
    return kb_mod.KnowledgeBase(dirs=dirs, code_dirs=code_dirs, top_k=cfg.knowledge.top_k)


def check(cfg) -> None:
    print(f"engine     : {cfg.engine}")
    print(f"base_url   : {cfg.api.base_url}")
    print(f"model      : {cfg.api.model}")
    print(f"api_key    : {'已设置' if cfg.api.api_key else '未设置(' + cfg.api.api_key_env + ')'}")
    print(f"prompts    : default={'有' if 'default' in cfg.prompts else '无'}, routes={len(cfg.routes)} 条")
    print(f"listen     : {cfg.listen or '全部会话'}")
    feats = cfg.features
    print(f"features   : links={feats.read_links} time={feats.time_context} emoji={feats.emotions}")
    print(f"memory     : {'开' if cfg.memory.enabled else '关'} dir={cfg.memory.dir} max={cfg.memory.max_history}")
    kb = make_kb(cfg)
    kb.reload(force=True)
    print(f"knowledge  : {'开' if cfg.knowledge.enabled else '关'} chunks={len(kb._chunks)}")
    for d in kb.dirs:
        print(f"  doc  {d}  ({'存在' if d.is_dir() else '不可达'})")
    for d in kb.code_dirs:
        print(f"  code {d}  ({'存在' if d.is_dir() else '不可达'})")
    if cfg.engine == "api":
        reply = llm.ask(cfg, llm.SYSTEM_HINT, "回复“ok”两个字母即可")
        print(f"模型连通性 : {reply[:60]}")


def handle(cfg, wx, mem, chat: str, text: str, sender: str, kb=None) -> None:
    """一条完整链路：链接增强 → 记忆/时间/知识库上下文 → LLM → 节流发送（纯文本，DB-only）。"""
    enriched = webpage.enrich(cfg, text)
    question = llm.build_question(cfg, mem, chat, sender, enriched, kb=kb)
    system = router.system_prompt_for(cfg, chat)
    reply = llm.ask(cfg, system, question)

    body = reply.strip()
    lo, hi = cfg.rate.send_interval
    if body:
        time.sleep(random.uniform(lo, hi))
        wx.send(chat, body)

    mem.append(chat, sender, text)
    if mem.needs_summarize(chat):
        old_summary, recent = mem.load(chat)
        half = len(recent) // 2
        new_summary = llm.summarize(cfg, ([old_summary] if old_summary else []) + recent[:half])
        if new_summary:
            mem.rewrite(chat, new_summary, recent[half:])
            log.info("会话 %s 记忆已压缩（%d → %d 条）", chat, len(recent), len(recent[half:]))


def _kb_watchdog(kb, interval: float = 30.0) -> None:
    """后台守护：每 interval 秒查一次 mtime，知识库文件变了自动重建索引。"""
    while True:
        time.sleep(interval)
        try:
            kb.refresh()
        except Exception as exc:  # noqa: BLE001
            log.warning("知识库守护异常: %s", exc)


def run(cfg) -> None:
    from bot.wechat import WeChat  # 延迟导入：--check 不需要 wxauto

    wx = WeChat()
    mem = mem_mod.SessionMemory(cfg)
    kb = make_kb(cfg) if cfg.knowledge.enabled else None
    if kb:
        kb.reload(force=True)            # 启动即建索引，首问不卡
        threading.Thread(target=_kb_watchdog, args=(kb,), daemon=True).start()
    last_seen: dict[str, str] = {}
    pending: dict[str, tuple[str, str, float]] = {}   # chat → (text, sender, deadline)
    log.info("进入轮询循环，Ctrl+C 退出")
    while True:
        now = time.monotonic()
        for chat in wx.unread_chats():
            if not router.should_listen(cfg, chat):
                continue
            msgs = wx.read_latest(chat)
            if not msgs:
                continue
            text = "\n".join(m.text for m in msgs if m.text)
            if text == last_seen.get(chat):
                continue  # 已回过，去重
            last_seen[chat] = text
            # 合并窗口：窗口期内新消息只刷新快照与截止时间，静默后才回答
            sender = msgs[-1].sender
            prev = pending.get(chat)
            if prev:
                sender = prev[1] or sender
            pending[chat] = (text, sender, now + cfg.rate.merge_window_seconds)
        due = [c for c, (_, _, dl) in pending.items() if dl <= now]
        for chat in due:
            text, sender, _ = pending.pop(chat)
            handle(cfg, wx, mem, chat, text, sender, kb=kb)
        time.sleep(cfg.rate.poll_seconds)


# ── 企业微信智能机器人回调服务 ──────────────────────────
def serve(cfg) -> None:
    from bot.wecom import BotService, build_reply, check_signature, parse_message

    mem = mem_mod.SessionMemory(cfg)
    kb = make_kb(cfg) if cfg.knowledge.enabled else None
    if kb:
        kb.reload(force=True)
        threading.Thread(target=_kb_watchdog, args=(kb,), daemon=True).start()
    service = BotService(cfg, kb, mem)

    token = cfg.wecom.token

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):                      # URL 验证
            qs = parse_qs(urlparse(self.path).query)
            sig = qs.get("signature", [""])[0]
            ts = qs.get("timestamp", [""])[0]
            nonce = qs.get("nonce", [""])[0]
            echo = qs.get("echostr", [""])[0]
            if check_signature(token, ts, nonce, echo, sig):
                log.info("URL 验证通过")
                self._send(200, echo)          # 明文回显
            else:
                log.warning("URL 验证失败")
                self._send(403, "forbidden")

        def do_POST(self):                     # 消息回调
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
            inc = parse_message(raw)
            if inc is None or not inc.text:
                self._send(200, '{"msgtype":"empty"}')
                return
            reply = service.handle_text(inc)
            body = build_reply(reply) if reply else '{"msgtype":"empty"}'
            self._send(200, body)
            log.info("[%s] %s → %s", inc.name or inc.userid, inc.text[:30], (reply or "(dup)")[:50])

        def log_message(self, fmt, *args):     # 静音默认 access log
            log.debug(fmt, *args)

    host, port = cfg.wecom.host, cfg.wecom.port
    httpd = ThreadingHTTPServer((host, port), Handler)
    log.info("企业微信回调服务已启动 http://%s:%d/  stats=%s", host, port, service.stats)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


def warm(cfg, keywords: list[str]) -> None:
    """离峰建库：走面板截图存 stickers/。（面板依赖前台，默认不在主链路。）"""
    from bot.wechat import WeChat

    wx = WeChat()
    wx.focus("文件传输助手")
    for kw in keywords:
        if emotion.pick_image(kw):
            print(f"skip {kw}（已在库）")
            continue
        ok = emotion.send_from_panel(kw)
        print(f"{'ok ' if ok else 'fail'} {kw}")
        time.sleep(1.0)


def setup_logging() -> None:
    fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)
    log_dir = cfg_mod.ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    fh = logging.handlers.TimedRotatingFileHandler(
        log_dir / "wxbot.log", when="midnight", backupCount=7, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)


def main() -> None:
    parser = argparse.ArgumentParser(description="wxbot-mini")
    parser.add_argument("--check", action="store_true", help="只做配置与连通性自检")
    parser.add_argument("--serve", action="store_true", help="企业微信智能机器人 HTTP 回调服务")
    parser.add_argument("--warm", nargs="*", metavar="关键词", help="离峰批量建表情库，如 --warm 加油 晚安")
    args = parser.parse_args()

    setup_logging()
    cfg = cfg_mod.load()
    if args.check:
        check(cfg)
        return
    if args.warm is not None:
        kws = args.warm or ["开心", "收到", "加油"]
        warm(cfg, kws)
        return
    if args.serve:
        serve(cfg)
        return
    try:
        run(cfg)
    except KeyboardInterrupt:
        print("bye")


if __name__ == "__main__":
    main()
