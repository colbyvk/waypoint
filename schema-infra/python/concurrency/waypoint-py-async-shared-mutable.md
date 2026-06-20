# `waypoint-py-async-shared-mutable`

> Beacon schema — generated from `infra/python/concurrency/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** python

## Agent hypothesis
> async mutation of shared state with no lock held — data race on a value-bearing structure?

## Where the detection code lives
- **Rule:** [`infra/python/concurrency/python.yaml`](../../../infra/python/concurrency/python.yaml) — Semgrep rule `waypoint-py-async-shared-mutable`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-async-shared-mutable`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-async-shared-mutable", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "abuse"], "severity_prior": 0.6,
    "hypothesis": "async mutation of shared state with no lock held — data race on a value-bearing structure?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-async-shared-mutable" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/py-async-shared-mutable.md`](../../../hazards/py-async-shared-mutable.md)
