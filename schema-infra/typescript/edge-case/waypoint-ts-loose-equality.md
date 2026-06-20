# `waypoint-ts-loose-equality`

> Beacon schema — generated from `infra/typescript/edge-case/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> loose == / != — coercion produces a wrong comparison result?

## Where the detection code lives
- **Rule:** [`infra/typescript/edge-case/typescript-hardening.yaml`](../../../infra/typescript/edge-case/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-loose-equality`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-loose-equality`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-loose-equality", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "loose == / != — coercion produces a wrong comparison result?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-loose-equality" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-loose-equality
  return a == b;
}
```
