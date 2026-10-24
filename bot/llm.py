"""大模型调用：api 档直调 OpenAI 兼容接口；dsh 档走 dsh headless 子进程。"""
from __future__ import annotations

import json
import logging
import subprocess
import urllib.request

from .config import Config

log = logging.getLogger("wxbot.llm")

SYSTEM_HINT = (
    "你在替一个真人回复微信消息。直接给出可发送的回复文本本身，"
    "不要解释、不要加引号或前后缀。"
)


def _ask_api(cfg: Config, history: list[dict], question: str) -> str:
    url = cfg.api.base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": cfg.api.model,
        "messages": [
            {"role": "system", "content": SYSTEM_HINT},
            *history,
            {"role": "user", "content": question},
        ],
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
    return data["choices"][0]["message"]["content"].strip()


def _ask_dsh(cfg: Config, question: str) -> str:
    cmd = [cfg.dsh.command, *cfg.dsh.args, question]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=cfg.api.timeout_seconds + 30)
    return out.stdout.strip()


def ask(cfg: Config, history: list[dict], question: str) -> str:
    """返回模型回复文本；失败时返回简短错误说明，保证调用方可直接发送。"""
    try:
        if cfg.engine == "dsh":
            return _ask_dsh(cfg, question) or "（模型返回为空）"
        return _ask_api(cfg, history, question) or "（模型返回为空）"
    except Exception as exc:  # noqa: BLE001
        log.warning("LLM 调用失败: %s", exc)
        return f"（稍后回复你，刚才接口超时：{exc.__class__.__name__}）"
