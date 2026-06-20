# `waypoint-py-thread-shared-mutable-nolock`

> Beacon schema — generated from `infra/python/concurrency/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** python

## Agent hypothesis
> module-level dict/list/counter mutated in a def with no lock — data race under threads?

## Where the detection code lives
- **Rule:** [`infra/python/concurrency/python-hardening2.yaml`](../../../infra/python/concurrency/python-hardening2.yaml) — Semgrep rule `waypoint-py-thread-shared-mutable-nolock`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-thread-shared-mutable-nolock`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-thread-shared-mutable-nolock", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "abuse"], "severity_prior": 0.6,
    "hypothesis": "module-level dict/list/counter mutated in a def with no lock — data race under threads?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-thread-shared-mutable-nolock" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-thread-shared-mutable-nolock
    HIT_COUNTS[key] = HIT_COUNTS.get(key, 0) + 1

```
