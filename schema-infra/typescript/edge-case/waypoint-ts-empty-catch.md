# `waypoint-ts-empty-catch`

> Beacon schema — generated from `infra/typescript/edge-case/typescript.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> empty catch — a dropped error that should be handled?

## Where the detection code lives
- **Rule:** [`infra/typescript/edge-case/typescript.yaml`](../../../infra/typescript/edge-case/typescript.yaml) — Semgrep rule `waypoint-ts-empty-catch`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-empty-catch`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-empty-catch", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "empty catch — a dropped error that should be handled?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-empty-catch" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
