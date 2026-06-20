# Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

HITS = {}
TOTAL = 0
RESULTS = []


async def record_hit(key):
    # WAYPOINT-PLANT: PY-ASYNC-SHARED [axes: concurrency,abuse]
    HITS[key] = HITS.get(key, 0) + 1
    await asyncio.sleep(0)
    return HITS[key]


_lock = asyncio.Lock()


async def record_hit_safe(key):
    # WAYPOINT-OK: async handler guarded by asyncio.Lock
    async with _lock:
        HITS[key] = HITS.get(key, 0) + 1
    return HITS[key]


def bump():
    global TOTAL
    # WAYPOINT-PLANT: PY-THREAD-SHARED [axes: concurrency]
    TOTAL += 1


def run_threads():
    with ThreadPoolExecutor(max_workers=8) as ex:
        for _ in range(100):
            ex.submit(bump)
    t = threading.Thread(target=bump)
    t.start()


async def worker(i):
    # WAYPOINT-PLANT: PY-ASYNC-GATHER-WRITE [axes: concurrency]
    RESULTS.append(i)


async def run_all():
    await asyncio.gather(*[worker(i) for i in range(50)])
