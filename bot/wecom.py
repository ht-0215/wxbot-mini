"""企业微信智能机器人回调服务（API 模式）。

路由：
    GET  /        URL 验证：sha1(token,timestamp,nonce,echostr) 比对签名后回显 echostr
    POST /        消息回调：解析 JSON（容错 XML），提问走 知识库+LLM，同步回复 markdown

智能机器人推送为 JSON：{"from":{"userid","name"},"msgtype":"text","text":{"content"},...}
回复体：{"msgtype":"markdown","markdown":{"content":"..."}}
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass

log = logging.getLogger("wxbot.wecom")


@dataclass
class Incoming:
    userid: str
    name: str
    text: str


def check_signature(token: str, timestamp: str, nonce: str, echostr: str, signature: str) -> bool:
    """企业微信签名：四个值排序拼接后 sha1。token 未配置时直接放行。"""
    if not token:
        return True
    items = sorted([token, timestamp, nonce, echostr])
    digest = hashlib.sha1("".join(items).encode("utf-8")).hexdigest()
    return digest == signature


def parse_message(body: str) -> Incoming | None:
    """解析消息体，JSON 优先、XML 兜底；取不到文本返回 None。"""
    body = body.strip()
    if not body:
        return None
    try:
        data = json.loads(body)
        if isinstance(data, dict):
            frm = data.get("from") or {}
            if isinstance(frm, str):
                frm = {"userid": frm}
            text = ""
            for key in ("text", "msg"):
                v = data.get(key)
                if isinstance(v, dict):
                    text = str(v.get("content") or v.get("value") or "").strip()
                elif isinstance(v, str):
                    text = v.strip()
                if text:
                    break
            return Incoming(
                userid=str(frm.get("userid") or data.get("openid") or ""),
                name=str(frm.get("name") or ""),
                text=text,
            )
    except (json.JSONDecodeError, TypeError):
        pass
    # XML 兜底：<xml><FromUserName>..</FromUserName><Content>..</Content></xml>
    def tag(name: str) -> str:
        m = re.search(rf"<{name}><!\[CDATA\[(.*?)\]\]></{name}>|<{name}>(.*?)</{name}>", body, re.S)
        if not m:
            return ""
        return (m.group(1) or m.group(2) or "").strip()

    text = tag("Content")
    if not text:
        return None
    return Incoming(userid=tag("FromUserName"), name=tag("FromUserName"), text=text)


def build_reply(reply: str) -> str:
    return json.dumps(
        {"msgtype": "markdown", "markdown": {"content": reply}},
        ensure_ascii=False,
    )


class BotService:
    """把回调与推理层粘合：问 → (知识库+记忆+LLM) → 答。"""

    def __init__(self, cfg, kb, mem, answer_fn=None) -> None:
        from bot.scheduler import Scheduler

        self.cfg = cfg
        self.kb = kb
        self.mem = mem
        self._answer = answer_fn
        self.sched = Scheduler(send=self._queue_push)
        self._pending: dict[str, list[str]] = {}        # chat → 到期待推文本
        self._cache: dict[str, tuple[float, str]] = {}   # userid → (ts, 上次消息)
        self._cache_ttl = 120.0
        self.stats = {"recv": 0, "reply": 0, "dup": 0, "err": 0}

    def _queue_push(self, chat: str, text: str) -> None:
        """HTTP 回调无法异步推送：到期文本排队，随该用户下一条请求一起回。"""
        self._pending.setdefault(chat, []).append(text)

    def handle_text(self, inc: Incoming) -> str:
        self.stats["recv"] += 1
        text = inc.text
        now = time.monotonic()
        prev = self._cache.get(inc.userid)
        if prev and prev[1] == text and now - prev[0] < self._cache_ttl:
            self.stats["dup"] += 1          # 重复投递：不再重新生成，回空串
            return ""
        try:
            reply = self._answer_text(inc, text)
        except Exception as exc:  # noqa: BLE001
            self.stats["err"] += 1
            log.warning("生成失败: %s", exc)
            reply = ""            # 静默：不把内部故障文案发给客户，只记日志
        self._cache[inc.userid] = (now, text)
        self.stats["reply"] += 1
        chat_key = inc.name or inc.userid or "wecom"
        queued = self._pending.pop(chat_key, [])
        if queued and reply:
            reply += "\n\n" + "\n".join(queued)
        elif queued:
            reply = "\n".join(queued)
        return reply

    def _answer_text(self, inc: Incoming, text: str) -> str:
        from bot import commands, llm, router

        chat = inc.name or inc.userid or "wecom"
        cmd = commands.dispatch(self.cfg, self.mem, self.kb, chat, text,
                                guard=getattr(self, "guard", None))
        if cmd is not None:
            return cmd
        note = self.sched.add(chat, text)
        if note is not None:
            return note
        question = llm.build_question(self.cfg, self.mem, chat, inc.name, text, kb=self.kb)
        system = router.system_prompt_for(self.cfg, chat)
        reply = llm.ask(self.cfg, system, question)
        self.mem.append(chat, inc.name, text)
        return reply
