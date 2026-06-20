# `waypoint-ts-logic-sort-no-comparator`

> Beacon schema — generated from `infra/typescript/logic/typescript-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** logic
- **Language(s):** typescript

## Agent hypothesis
> Array.sort() with no comparator — lexicographic order is wrong for numbers; confirm element type.

## Where the detection code lives
- **Rule:** [`infra/typescript/logic/typescript-logic.yaml`](../../../infra/typescript/logic/typescript-logic.yaml) — Semgrep rule `waypoint-ts-logic-sort-no-comparator`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-logic-sort-no-comparator`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-logic-sort-no-comparator", "level": "note",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.3,
    "hypothesis": "Array.sort() with no comparator — lexicographic order is wrong for numbers; confirm element type.",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-logic-sort-no-comparator" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/logic_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-logic-sort-no-comparator
  return nums.sort();
}
```
