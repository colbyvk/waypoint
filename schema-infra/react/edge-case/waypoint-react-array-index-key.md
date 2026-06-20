# `waypoint-react-array-index-key`

> Beacon schema — generated from `infra/react/edge-case/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> array index used as React key in a .map() — state/DOM corruption on reorder?

## Where the detection code lives
- **Rule:** [`infra/react/edge-case/react-hardening.yaml`](../../../infra/react/edge-case/react-hardening.yaml) — Semgrep rule `waypoint-react-array-index-key`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-array-index-key`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-array-index-key", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "array index used as React key in a .map() — state/DOM corruption on reorder?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-array-index-key" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
        // WAYPOINT-PLANT: waypoint-react-array-index-key [axes: edge-case]
        return <li key={i}>{item}</li>;
      })}
```
