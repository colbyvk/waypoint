# `waypoint-ts-logic-constant-condition`

> Beacon schema — generated from `infra/typescript/logic/typescript-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** logic
- **Language(s):** typescript

## Agent hypothesis
> constant if-condition (if (true) / if (false)) — dead branch or leftover toggle?

## Where the detection code lives
- **Rule:** [`infra/typescript/logic/typescript-logic.yaml`](../../../infra/typescript/logic/typescript-logic.yaml) — Semgrep rule `waypoint-ts-logic-constant-condition`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-logic-constant-condition`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-logic-constant-condition", "level": "note",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.3,
    "hypothesis": "constant if-condition (if (true) / if (false)) — dead branch or leftover toggle?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-logic-constant-condition" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/logic_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-logic-constant-condition
  if (true) {
    return 1;
```
