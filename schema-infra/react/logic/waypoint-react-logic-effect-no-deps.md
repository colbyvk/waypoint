# `waypoint-react-logic-effect-no-deps`

> Beacon schema — generated from `infra/react/logic/react-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** typescript

## Agent hypothesis
> useEffect with no dependency array — runs every render; missing `[]` or explicit deps?

## Where the detection code lives
- **Rule:** [`infra/react/logic/react-logic.yaml`](../../../infra/react/logic/react-logic.yaml) — Semgrep rule `waypoint-react-logic-effect-no-deps`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-logic-effect-no-deps`
- **Also flagged by (when that tool is installed):** eslint `react-hooks/exhaustive-deps`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-logic-effect-no-deps", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "useEffect with no dependency array — runs every render; missing `[]` or explicit deps?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-logic-effect-no-deps" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/LogicSamples.tsx
  // WAYPOINT-PLANT: waypoint-react-logic-effect-no-deps
  useEffect(() => {
    console.log(id);
```
