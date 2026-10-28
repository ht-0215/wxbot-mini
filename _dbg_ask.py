import logging
import traceback

logging.basicConfig(level=logging.WARNING)
from bot import config, llm

cfg = config.load()
try:
    r = llm.ask(cfg, "你是助手", "sdk 怎么编译")
    print("ANS:", r[:120])
except Exception:
    traceback.print_exc()
