# `waypoint-ts-unguarded-computed-index`

> Beacon schema — generated from `infra/typescript/edge-case/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> arr[computedIndex].prop — index out of range yields undefined, property read throws?

## Where the detection code lives
- **Rule:** [`infra/typescript/edge-case/typescript-hardening2.yaml`](../../../infra/typescript/edge-case/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-unguarded-computed-index`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-unguarded-computed-index`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-unguarded-computed-index", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "arr[computedIndex].prop — index out of range yields undefined, property read throws?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-unguarded-computed-index" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-unguarded-computed-index
  return parts[idx].toUpperCase();
}
```
