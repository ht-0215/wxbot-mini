"""调试：baudrate chunk 在 BM25 / vec / fused 三路中的位次。"""
import logging
import time

logging.basicConfig(level=logging.ERROR)

from bot import config
from bot.knowledge import _tokens_of
from run import make_kb

cfg = config.load()
cfg.knowledge.hybrid = True
kb = make_kb(cfg)
kb.reload(force=True)
dl = time.monotonic() + 120
while time.monotonic() < dl:
    v = kb._vec
    if v is not None and v.vecs is not None and v.model is not None:
        break
    time.sleep(2)

q = "镜像烧写时串口波特率设多少"
targets = [i for i, c in enumerate(kb._chunks)
           if "baudrate:115200" in c.body and "镜像烧写" in c.source]
print("RES targets:", [(i, kb._chunks[i].title[:16]) for i in targets])

vt = kb._vec.top(q, len(kb._chunks), k=20)
for rank, (i, s) in enumerate(sorted(vt, key=lambda t: -t[1])):
    mark = "<==" if i in targets else ""
    print("RES vec rank%d %.3f %s %s | %s" % (rank, s, i, mark, kb._chunks[i].title[:20]))

hits = kb.search(q, top_k=4)
print("RES fused:", [(h.source.split('/')[-1][:28], h.title[:14]) for h in hits])
