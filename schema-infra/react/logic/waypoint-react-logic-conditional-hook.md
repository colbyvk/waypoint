# `waypoint-react-logic-conditional-hook`

> Beacon schema — generated from `infra/react/logic/react-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** typescript

## Agent hypothesis
> hook (use*) called inside an if-block — Rules of Hooks violation; state desync / runtime crash?

## Where the detection code lives
- **Rule:** [`infra/react/logic/react-logic.yaml`](../../../infra/react/logic/react-logic.yaml) — Semgrep rule `waypoint-react-logic-conditional-hook`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-logic-conditional-hook`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-logic-conditional-hook", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "hook (use*) called inside an if-block — Rules of Hooks violation; state desync / runtime crash?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-logic-conditional-hook" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/LogicSamples.tsx
  // WAYPOINT-PLANT: waypoint-react-logic-conditional-hook
  if (enabled) {
    const [n, setN] = useState(0);
```
