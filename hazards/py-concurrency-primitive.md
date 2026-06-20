# Concurrency primitive in use (Python)

- **Axes:** concurrency
- **Languages:** Python
- **Generated rule(s):** `waypoint-py-concurrency-primitive`
- **Agent hypothesis:** "concurrency primitive present — unsynchronized shared-state access nearby?"

## What it is
This is a low-key "beacon" rule. It does nothing more than notice that the code uses a
tool for running things at the same time: `threading.Thread`,
`multiprocessing.Process`, a `ThreadPoolExecutor`/`ProcessPoolExecutor`, or one of
`asyncio.gather` / `asyncio.create_task` / `asyncio.ensure_future`. The mere
presence of these is not a problem — it is the *entry ticket* for concurrency bugs.
The flag exists so the agent knows "this region runs work in parallel" and can then
ask the real question: is any shared state read or written here without
synchronization? It is a pure proxy: a marked region is usually perfectly fine.

## Bad (flagged)
```python
# samples/monorepo/py_service/workers.py
async def run_all():
    await asyncio.gather(*[worker(i) for i in range(50)])  # primitive present

def run_threads():
    with ThreadPoolExecutor(max_workers=8) as ex:          # primitive present
        for _ in range(100):
            ex.submit(bump)
```

## Acceptable (not a problem)
```python
# Using a primitive is fine when nothing shared is mutated unsafely.
# (No dedicated WAYPOINT-OK control exists for this beacon; minimal example below.)
async def run_all_safe(items):
    # gather over pure functions: each task owns its result, nothing shared written
    return await asyncio.gather(*[double(i) for i in items])

async def double(i):
    return i * 2
```

## Notes for the agent
- This rule fires on the *primitive itself*, by design, so almost every match is
  "fine until proven otherwise." Treat it as a pointer, not an accusation.
- **Confirms a real concern:** the parallel work touches a module global, a shared
  collection, a file, or a connection without a lock or other coordination.
- **Dismisses it:** each unit of work is independent and only returns its own
  result, or all shared access is already guarded.
