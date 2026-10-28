"""配置加载：读取 config.yaml，环境变量解析成最终值。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.yaml"


def reload_into(cfg: Config, path: Path | None = None) -> bool:
    """重读 YAML 并原地替换 cfg 的各字段（保持对象引用不变）。mtime 没变返回 False。"""
    path = path or DEFAULT_CONFIG
    try:
        m = path.stat().st_mtime
    except OSError:
        return False
    if getattr(cfg, "_mtime", 0.0) == m:
        return False
    fresh = load(path)
    for f in ("engine", "api", "dsh", "rate", "features", "memory",
              "knowledge", "wecom", "window", "prompts", "routes",
              "listen", "at_names"):
        setattr(cfg, f, getattr(fresh, f))
    cfg._mtime = m
    return True


@dataclass
class ApiCfg:
    base_url: str = "http://127.0.0.1:4000/v1"
    model: str = "wx_40b"
    api_key_env: str = "WX40B_API_KEY"
    timeout_seconds: int = 120
    max_tokens: int = 700           # 答复封顶，控尾延；FAE 结论通常 300~500

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
    hybrid: bool = True             # BM25+向量混合重排；无模型自动退纯 BM25


@dataclass
class WecomCfg:
    """企业微信智能机器人回调服务（--serve）。"""
    host: str = "0.0.0.0"
    port: int = 8090
    token: str = ""                 # 管理后台回调配置的 Token，留空则跳过签名校验


@dataclass
class WindowCfg:
    """双开微信时绑定 bot 使用的窗口：hwnd 优先，其次 title；都空=跟随默认。"""
    hwnd: int = 0
    title: str = ""


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
    wecom: WecomCfg = field(default_factory=WecomCfg)
    window: WindowCfg = field(default_factory=WindowCfg)
    prompts: Dict[str, str] = field(default_factory=dict)
    routes: Dict[str, str] = field(default_factory=dict)
    listen: List[str] = field(default_factory=list)
    at_names: List[str] = field(default_factory=list)   # 群内需 @ 这些名字才回复


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
    wc_d = raw.get("wecom") or {}
    wd_d = raw.get("window") or {}

    cfg = Config(
        engine=str(llm.get("engine", "api")),
        api=ApiCfg(
            base_url=api_d.get("base_url", ApiCfg.base_url),
            model=api_d.get("model", ApiCfg.model),
            api_key_env=api_d.get("api_key_env", ApiCfg.api_key_env),
            timeout_seconds=int(api_d.get("timeout_seconds", 120)),
            max_tokens=int(api_d.get("max_tokens", 700)),
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
        wecom=WecomCfg(
            host=str(wc_d.get("host", "0.0.0.0")),
            port=int(wc_d.get("port", 8090)),
            token=str(wc_d.get("token", "")),
        ),
        window=WindowCfg(
            hwnd=int(wd_d.get("hwnd", 0) or 0),
            title=str(wd_d.get("title", "") or ""),
        ),
        prompts=dict(raw.get("prompts") or {}),
        routes=dict(raw.get("routes") or {}),
        listen=list(raw.get("listen") or []),
        at_names=list(raw.get("at_names") or []),
    )
    try:
        cfg._mtime = path.stat().st_mtime
    except OSError:
        cfg._mtime = 0.0
    return cfg
