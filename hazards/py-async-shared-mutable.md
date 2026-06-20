# Async mutation of shared state with no lock (Python)

- **Axes:** concurrency, abuse
- **Languages:** Python
- **Generated rule(s):** `waypoint-py-async-shared-mutable`
- **Agent hypothesis:** "async mutation of shared state with no lock held — data race on a value-bearing structure?"

## What it is
Inside an `async def`, code changes a piece of state that lives outside the
function — a module-level dictionary, list, or counter — and there is no lock held
around the change. Because many async tasks can be in flight at once and hand
control back and forth at every `await`, two of them can read-modify-write the same
value and lose an update. This flag marks the *region*; it does **not** prove a race
happened. It tells the agent: "concurrency and a shared write meet here — go look."

## Bad (flagged)
```python
# samples/monorepo/py_service/workers.py
HITS = {}

async def record_hit(key):
    HITS[key] = HITS.get(key, 0) + 1   # read-modify-write on shared dict, no lock
    await asyncio.sleep(0)
    return HITS[key]
```

## Acceptable (not a problem)
```python
# samples/monorepo/py_service/workers.py
_lock = asyncio.Lock()

async def record_hit_safe(key):
    async with _lock:                  # the shared write is serialized by a lock
        HITS[key] = HITS.get(key, 0) + 1
    return HITS[key]
```

## Notes for the agent
- **Confirms it:** the mutated name is genuinely shared (module global, class
  attribute, captured closure) AND more than one task can run this code
  concurrently AND there is an `await` between the read and the write.
- **Dismisses it:** the state is local to one task, the value is only ever read,
  or the whole region is already inside an `async with lock:` / `with lock:`.
- Writing to `self.<attr>` is excluded by the rule — per-instance state is usually
  not the shared thing. Still worth a glance if instances are shared across tasks.
