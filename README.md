# wxbot-mini

微信 PC 端自动回复机器人：监听未读消息，按会话路由到不同的 system prompt，
调用 OpenAI 兼容大模型（默认 wx_40b）生成回复并发回。

参考 [KouriChat / wechatbot-new](https://github.com/fanyuantaier/wechatbot-new) 的消息路由、
链接读取、记忆压缩、情绪表情包与节流设计，做了三点精简：无 WebUI（配置即 `config.yaml`）、
推理端可插拔（api / dsh 两档）、依赖收窄到 wxauto + PyYAML。

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

## 功能

| 功能 | 开关 (`features.`) | 说明 |
|---|---|---|
| 会话级 Prompt | `routes` / `prompts.default` | 每个联系人/群独立 system prompt，未命中走 default |
| 监听名单 | `listen` | 留空回复全部；填名单只回复列表内会话 |
| 链接读取 | `read_links` | 消息里的 http(s) 链接抓正文摘要拼进提问 |
| 时间感知 | `time_context` | 每次提问附带"年-月-日 星期 时:分" |
| 会话记忆 | `memory.*` | 每会话一个 md：最近 N 条进上下文，超过 `summarize_after` 自动摘要压缩 |
| 情绪表情包 | `emotions` / `emotion_mode` | 默认关；hybrid 只查 `stickers/` 本地库秒发，冷词离峰 `--warm` 建库 |
| 知识库检索 | `knowledge.*` | 见下节，FAE 技术支持核心 |
| 节流合并 | `rate.*` | 轮询间隔 + 发送前随机间隔，降低风控风险 |

`llm.engine` 两档：`api` 直调 wx_40b 网关；`dsh` 走 `dsh headless`，
复用 DSH 的 skill / 工具能力（如串口调试、office 文档类技能）。

## 知识库（FAE 核心）

多根检索：`dir`（项目内 knowledge/）+ `extra_dirs`（文档 UNC）+ `code_dirs`（源码子集）。

- 文档按 `#/##/###` 标题切段；tex 自动转轻 markdown；md/txt/rst/tex 四种格式
- 源码（c/h/dts/dtsi）按顶层函数/宏切段，标题取函数名，可直接问"phy_nocxn 是哪来的"
- 检索：倒排索引出候选 → BM25 计分（稀有词权重高、tf 饱和、长度归一），
  标识符自动拆子词（`phy_nocxn`→phy+nocxn）、文件名可搜、同文件最多 2 段防霸屏
- WSL UNC 路径注意用 YAML 单引号（双引号会折叠 `\\` 前缀）
- mtime 变化自动重建；UNC 遍历慢，运行期 300s TTL，启动 force 一次（全量约 1 分钟）
- 建议只挂关心的子目录（arch/csky、drivers/net/phy），整棵内核树首载会到分钟级

## 配置

全部在 `config.yaml`，字段说明见文件内注释。key 只写环境变量名（`api_key_env`），
不把密钥写进文件。

## 结构

```
run.py             主循环 + handle()：链接 → 记忆/时间/知识库 → LLM → 节流发送
bot/config.py      YAML + 环境变量 → Config
bot/router.py      会话名 → prompt；监听名单过滤
bot/llm.py         api / dsh 两档推理；提问拼装；摘要压缩
bot/memory.py      memory/<会话>.md：摘要 + 最近消息，超量压缩
bot/knowledge.py   多根知识库：标题/函数切段 + BM25 倒排检索
bot/webpage.py     链接提取 + 正文纯文本抓取（html.parser，无额外依赖）
bot/emotion.py     [标签] 解析 + stickers/ 表情库 + 面板建库(--warm)
bot/wechat.py      wxauto/wechatauto 封装：unread_chats / read_latest / send / send_image
knowledge/         FAE 资料：common/（芯片指南、固件说明）+ 各客户目录
stickers/          表情图库：一词一图 png
```

## 已知约束

- 仅 Windows；wxauto 依赖 UIA，需保持 PC 微信已登录并最小化到托盘
- 微信客户端版本与 wxauto 兼容性绑定，建议关闭微信自动更新
- 自己发出的消息不会再次触发回复（按会话 last_seen 去重）
- 表情包目录 `emojis/<情绪>/*.png|jpg|gif` 需自备；缺目录时只发文本
