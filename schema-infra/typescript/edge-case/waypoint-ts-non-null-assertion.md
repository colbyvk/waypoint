# `waypoint-ts-non-null-assertion`

> Beacon schema — generated from `infra/typescript/edge-case/typescript.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> non-null assertion (!) — can the value be null/undefined here?

## Where the detection code lives
- **Rule:** [`infra/typescript/edge-case/typescript.yaml`](../../../infra/typescript/edge-case/typescript.yaml) — Semgrep rule `waypoint-ts-non-null-assertion`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-non-null-assertion`
- **Also flagged by (when that tool is installed):** mypy (`union-attr`); eslint `@typescript-eslint/no-non-null-assertion`; mypy (`union-attr`, None-deref)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-non-null-assertion", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "non-null assertion (!) — can the value be null/undefined here?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-non-null-assertion" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
