# `waypoint-ts-logic-self-comparison`

> Beacon schema — generated from `infra/typescript/logic/typescript-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** typescript

## Agent hypothesis
> self-comparison ($X === $X / !==) is constant — likely a typo for a different operand?

## Where the detection code lives
- **Rule:** [`infra/typescript/logic/typescript-logic.yaml`](../../../infra/typescript/logic/typescript-logic.yaml) — Semgrep rule `waypoint-ts-logic-self-comparison`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-logic-self-comparison`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-logic-self-comparison", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "self-comparison ($X === $X / !==) is constant — likely a typo for a different operand?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-logic-self-comparison" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/logic_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-logic-self-comparison
  if (a === a) {
    return true;
```
