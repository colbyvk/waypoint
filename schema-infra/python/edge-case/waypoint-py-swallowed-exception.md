# `waypoint-py-swallowed-exception`

> Beacon schema — generated from `infra/python/edge-case/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> except…: pass — a dropped error that should be handled or logged?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python.yaml`](../../../infra/python/edge-case/python.yaml) — Semgrep rule `waypoint-py-swallowed-exception`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-swallowed-exception`
- **Also flagged by (when that tool is installed):** ruff `E722` (bare-except), `S110`, `BLE001` (blind-except)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-swallowed-exception", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "except…: pass — a dropped error that should be handled or logged?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-swallowed-exception" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
