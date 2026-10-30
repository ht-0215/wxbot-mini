"""大模型调用：api 档直调 OpenAI 兼容接口；dsh 档走 dsh headless 子进程。

提问文本按开关拼装：时间上下文 + 会话记忆 + 知识库检索段 + 链接摘要 + 原文。
"""
from __future__ import annotations

import json
import logging
import subprocess
import urllib.request
from datetime import datetime

from .config import Config
from .knowledge import KnowledgeBase
from .memory import SessionMemory

log = logging.getLogger("wxbot.llm")

SYSTEM_HINT = (
    "你是 FAE（现场应用工程师）技术支持助手。只依据【知识库参考】段落作答："
    "段落含具体命令/参数就直接引用给结论；段落只有概述没有细节时，"
    "如实说明未覆盖并指出应查的章节名，不要自行补全命令语法。"
    "简洁分点，直接输出回复文本本身，不要解释、不要加引号或前后缀。"
)

WEEKDAYS = "一二三四五六日"


def build_question(cfg: Config, mem: SessionMemory, chat: str, sender: str, text: str,
                   kb: KnowledgeBase | None = None) -> str:
    parts: list[str] = []
    if cfg.features.time_context:
        now = datetime.now()
        parts.append(f"[时间] {now:%Y-%m-%d} 周{WEEKDAYS[now.weekday()]} {now:%H:%M}")
    ctx = mem.context_block(chat)
    if ctx:
        parts.append(ctx)
    if kb is not None:
        kb_block = kb.context_block(text)
        if kb_block:
            parts.append(kb_block)
    who = f"{sender}: " if sender else ""
    parts.append(f"{who}{text}")
    return "\n".join(parts)


def _ask_api(cfg: Config, system: str, question: str) -> str:
    url = cfg.api.base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": cfg.api.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        # 答复封顶：FAE 结论 300~500 token 足够，限制长度也就是限制尾延
        "max_tokens": cfg.api.max_tokens,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.api.api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=cfg.api.timeout_seconds) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    content = ((choices[0] if choices else {}).get("message") or {}).get("content") if choices else None
    return (content or "").strip()


def _ask_dsh(cfg: Config, question: str) -> str:
    cmd = [cfg.dsh.command, *cfg.dsh.args, question]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=cfg.api.timeout_seconds + 30)
    return out.stdout.strip()


def ask(cfg: Config, system: str, question: str) -> str:
    """返回模型回复文本；空返回重试一次。

    失败/为空一律返回空串并记日志——调用方据此**静默**，不把内部占位文案
    （如"模型返回为空"）发给客户。
    """
    try:
        for attempt in range(2):
            if cfg.engine == "dsh":
                out = _ask_dsh(cfg, question)
            else:
                out = _ask_api(cfg, system, question)
            if out:
                return out
            log.info("模型返回为空%s", "，重试一次" if attempt == 0 else "")
        return ""
    except Exception as exc:  # noqa: BLE001
        log.warning("LLM 调用失败: %s", exc)
        return ""


def summarize(cfg: Config, old_lines: list[str]) -> str:
    """把旧消息行压成一段摘要文本，失败返回空串。"""
    joined = "\n".join(old_lines)
    prompt = f"把下面的聊天记录压缩成不超过120字的中文摘要，保留人名与关键事项：\n{joined}"
    try:
        if cfg.engine == "dsh":
            return _ask_dsh(cfg, prompt)
        return _ask_api(cfg, "你是摘要助手，只输出摘要本身。", prompt)
    except Exception as exc:  # noqa: BLE001
        log.warning("摘要失败: %s", exc)
        return ""
