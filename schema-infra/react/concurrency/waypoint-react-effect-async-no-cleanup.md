# `waypoint-react-effect-async-no-cleanup`

> Beacon schema — generated from `infra/react/concurrency/react.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, edge-case
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> async effect without cleanup — unmount/stale-closure race?

## Where the detection code lives
- **Rule:** [`infra/react/concurrency/react.yaml`](../../../infra/react/concurrency/react.yaml) — Semgrep rule `waypoint-react-effect-async-no-cleanup`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-effect-async-no-cleanup`
- **Also flagged by (when that tool is installed):** eslint `react-hooks/exhaustive-deps`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-effect-async-no-cleanup", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "edge-case"], "severity_prior": 0.6,
    "hypothesis": "async effect without cleanup — unmount/stale-closure race?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-effect-async-no-cleanup" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/react-effect-async-no-cleanup.md`](../../../hazards/react-effect-async-no-cleanup.md)
