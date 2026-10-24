# wxbot-mini

微信 PC 端自动回复机器人：监听未读消息，按会话路由到不同的 system prompt，
调用 OpenAI 兼容大模型（默认 wx_40b）生成回复并发回。

参考 [KouriChat / wechatbot-new](https://github.com/fanyuantaier/wechatbot-new) 的消息路由与节流设计，
做了三点精简：无 WebUI（配置即 `config.yaml`）、推理端可插拔（api / dsh 两档）、
依赖收窄到 wxauto + PyYAML。

## 快速开始

```powershell
pip install -r requirements.txt

# 1. 设置模型 key（二选一）
$env:WX40B_API_KEY = "sk-xxx"

# 2. 自检：打印配置 + 调一次模型，不碰微信
python run.py --check

# 3. 登录 PC 微信（保持后台运行），启动
python run.py
```

## 配置

全部在 `config.yaml`：

- `llm.engine` — `api` 直调模型接口；`dsh` 走 `dsh headless` 子进程，可复用 DSH 的 skill/工具
- `llm.api` — base_url / model / api_key_env（key 从环境变量读，不写死）
- `prompts.default` + `routes` — 按昵称/群名映射独立 prompt，未命中走 default
- `listen` — 只回复名单内会话；留空回复全部
- `rate` — 合并窗口 + 发送随机间隔（降低风控风险）

## 结构

```
run.py            主循环：轮询 → 去重 → 路由 → LLM → 节流发送
bot/config.py     YAML + 环境变量 → Config
bot/router.py     会话名 → prompt；监听名单过滤
bot/llm.py        api / dsh 两档推理，异常兜底成可发送文本
bot/wechat.py     wxauto 封装：unread_chats / read_latest / send
```

## 已知约束

- 仅 Windows；wxauto 依赖 UIA，需保持 PC 微信已登录并最小化到托盘
- 微信客户端版本与 wxauto 兼容性绑定，建议关闭微信自动更新
- 自己发出的消息不会再次触发回复（按会话 last_seen 去重）
