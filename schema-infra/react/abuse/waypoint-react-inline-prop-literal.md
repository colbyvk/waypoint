# `waypoint-react-inline-prop-literal`

> Beacon schema — generated from `infra/react/abuse/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** typescript

## Agent hypothesis
> inline arrow/object/array literal as a prop — new identity each render defeats memo and storms child re-renders?

## Where the detection code lives
- **Rule:** [`infra/react/abuse/react-hardening.yaml`](../../../infra/react/abuse/react-hardening.yaml) — Semgrep rule `waypoint-react-inline-prop-literal`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-inline-prop-literal`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-inline-prop-literal", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "inline arrow/object/array literal as a prop — new identity each render defeats memo and storms child re-renders?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-inline-prop-literal" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-inline-prop-literal [axes: abuse] */}
      <Child onClick={() => console.log("hi")} style={{ color: "red" }} rows={[1, 2, 3]} />

```
