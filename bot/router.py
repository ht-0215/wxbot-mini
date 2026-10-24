"""Prompt 路由：按昵称/群名选 system prompt，default 兜底。"""
from __future__ import annotations

from .config import Config


def system_prompt_for(cfg: Config, chat_name: str) -> str:
    """routes 的键先精确匹配，再做包含匹配；都不中走 prompts.default。"""
    routes = cfg.routes
    if chat_name in routes:
        return routes[chat_name]
    for key, prompt in routes.items():
        if key and (key in chat_name or chat_name in key):
            return prompt
    return cfg.prompts.get("default", "回答简洁、口语化，中文优先。")


def should_listen(cfg: Config, chat_name: str) -> bool:
    """listen 为空 = 全部会话；否则只回复名单内的。"""
    if not cfg.listen:
        return True
    return any(name in chat_name or chat_name in name for name in cfg.listen)
