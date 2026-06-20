# `waypoint-py-infinite-loop`

> Beacon schema — generated from `infra/python/abuse/python-loops.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** python

## Agent hypothesis
> infinite loop — reachable bounded exit, or a dead loop / busy-spin compute sink?

## Where the detection code lives
- **Rule:** [`infra/python/abuse/python-loops.yaml`](../../../infra/python/abuse/python-loops.yaml) — Semgrep rule `waypoint-py-infinite-loop`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-infinite-loop`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-infinite-loop", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "infinite loop — reachable bounded exit, or a dead loop / busy-spin compute sink?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-infinite-loop" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/loops.py
    # WAYPOINT-PLANT: waypoint-py-infinite-loop
    while True:
        time.sleep(1)
```
