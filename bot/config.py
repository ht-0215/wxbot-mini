"""配置加载：读取 config.yaml，环境变量解析成最终值。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"


@dataclass
class ApiCfg:
    base_url: str = "http://127.0.0.1:4000/v1"
    model: str = "wx_40b"
    api_key_env: str = "WX40B_API_KEY"
    timeout_seconds: int = 120

    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "")


@dataclass
class DshCfg:
    command: str = "dsh"
    args: List[str] = field(default_factory=lambda: ["headless"])


@dataclass
class RateCfg:
    poll_seconds: float = 3.0
    merge_window_seconds: float = 4.0
    send_interval: tuple = (1.5, 3.5)


@dataclass
class FeatureCfg:
    read_links: bool = True
    time_context: bool = True
    emotions: bool = False        # 表情包：FAE 技术支持场景默认关闭
    emotion_mode: str = "hybrid"  # hybrid: 只查 stickers/ 本地库秒发；panel: 允许面板补图


@dataclass
class KnowledgeCfg:
    enabled: bool = True
    dir: str = "knowledge"          # 单根目录（相对项目根）
    extra_dirs: List[str] = field(default_factory=list)  # 额外文档根，支持 WSL UNC 路径
    code_dirs: List[str] = field(default_factory=list)   # 源码根（c/h/dts），建议只挂子目录
    top_k: int = 3


@dataclass
class MemoryCfg:
    enabled: bool = True
    dir: str = "memory"
    max_history: int = 8
    summarize_after: int = 24


@dataclass
class Config:
    engine: str = "api"
    api: ApiCfg = field(default_factory=ApiCfg)
    dsh: DshCfg = field(default_factory=DshCfg)
    rate: RateCfg = field(default_factory=RateCfg)
    features: FeatureCfg = field(default_factory=FeatureCfg)
    memory: MemoryCfg = field(default_factory=MemoryCfg)
    knowledge: KnowledgeCfg = field(default_factory=KnowledgeCfg)
    prompts: Dict[str, str] = field(default_factory=dict)
    routes: Dict[str, str] = field(default_factory=dict)
    listen: List[str] = field(default_factory=list)


def load(path: Path | None = None) -> Config:
    path = path or DEFAULT_CONFIG
    raw: dict = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    llm = raw.get("llm") or {}
    api_d = llm.get("api") or {}
    dsh_d = llm.get("dsh") or {}
    rate_d = raw.get("rate") or {}
    feat_d = raw.get("features") or {}
    mem_d = raw.get("memory") or {}
    kb_d = raw.get("knowledge") or {}

    return Config(
        engine=str(llm.get("engine", "api")),
        api=ApiCfg(
            base_url=api_d.get("base_url", ApiCfg.base_url),
            model=api_d.get("model", ApiCfg.model),
            api_key_env=api_d.get("api_key_env", ApiCfg.api_key_env),
            timeout_seconds=int(api_d.get("timeout_seconds", 120)),
        ),
        dsh=DshCfg(command=dsh_d.get("command", "dsh"), args=list(dsh_d.get("args") or ["headless"])),
        rate=RateCfg(
            poll_seconds=float(rate_d.get("poll_seconds", 3.0)),
            merge_window_seconds=float(rate_d.get("merge_window_seconds", 4.0)),
            send_interval=tuple(rate_d.get("send_interval") or (1.5, 3.5)),
        ),
        features=FeatureCfg(
            read_links=bool(feat_d.get("read_links", True)),
            time_context=bool(feat_d.get("time_context", True)),
            emotions=bool(feat_d.get("emotions", False)),
            emotion_mode=str(feat_d.get("emotion_mode", "hybrid")),
        ),
        memory=MemoryCfg(
            enabled=bool(mem_d.get("enabled", True)),
            dir=str(mem_d.get("dir", "memory")),
            max_history=int(mem_d.get("max_history", 8)),
            summarize_after=int(mem_d.get("summarize_after", 24)),
        ),
        knowledge=KnowledgeCfg(
            enabled=bool(kb_d.get("enabled", True)),
            dir=str(kb_d.get("dir", "knowledge")),
            extra_dirs=[str(x) for x in (kb_d.get("extra_dirs") or [])],
            code_dirs=[str(x) for x in (kb_d.get("code_dirs") or [])],
            top_k=int(kb_d.get("top_k", 3)),
        ),
        prompts=dict(raw.get("prompts") or {}),
        routes=dict(raw.get("routes") or {}),
        listen=list(raw.get("listen") or []),
    )
