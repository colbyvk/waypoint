# `waypoint-py-concurrency-primitive`

> Beacon schema — generated from `infra/python/concurrency/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** python

## Agent hypothesis
> concurrency primitive present — unsynchronized shared-state access nearby?

## Where the detection code lives
- **Rule:** [`infra/python/concurrency/python.yaml`](../../../infra/python/concurrency/python.yaml) — Semgrep rule `waypoint-py-concurrency-primitive`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-concurrency-primitive`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-concurrency-primitive", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "concurrency primitive present — unsynchronized shared-state access nearby?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-concurrency-primitive" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/py-concurrency-primitive.md`](../../../hazards/py-concurrency-primitive.md)
