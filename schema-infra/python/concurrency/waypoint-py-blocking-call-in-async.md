# `waypoint-py-blocking-call-in-async`

> Beacon schema — generated from `infra/python/concurrency/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** python

## Agent hypothesis
> blocking call (time.sleep / requests.*) inside async def — event loop stalled?

## Where the detection code lives
- **Rule:** [`infra/python/concurrency/python-hardening.yaml`](../../../infra/python/concurrency/python-hardening.yaml) — Semgrep rule `waypoint-py-blocking-call-in-async`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-blocking-call-in-async`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-blocking-call-in-async", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.6,
    "hypothesis": "blocking call (time.sleep / requests.*) inside async def — event loop stalled?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-blocking-call-in-async" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-blocking-call-in-async
    time.sleep(5)
    return "done"
```
