# `waypoint-py-fire-and-forget-task`

> Beacon schema — generated from `infra/python/concurrency/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** python

## Agent hypothesis
> create_task() result discarded — task GC'd early or exceptions lost?

## Where the detection code lives
- **Rule:** [`infra/python/concurrency/python-hardening.yaml`](../../../infra/python/concurrency/python-hardening.yaml) — Semgrep rule `waypoint-py-fire-and-forget-task`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-fire-and-forget-task`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-fire-and-forget-task", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "create_task() result discarded — task GC'd early or exceptions lost?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-fire-and-forget-task" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-fire-and-forget-task
    asyncio.create_task(blocking_sleep_in_async())
    return "scheduled"
```
