# `waypoint-ts-promise-all-race`

> Beacon schema — generated from `infra/typescript/concurrency/typescript.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> Promise.all/race over concurrent ops — shared-state write race?

## Where the detection code lives
- **Rule:** [`infra/typescript/concurrency/typescript.yaml`](../../../infra/typescript/concurrency/typescript.yaml) — Semgrep rule `waypoint-ts-promise-all-race`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-promise-all-race`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-promise-all-race", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "Promise.all/race over concurrent ops — shared-state write race?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-promise-all-race" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
