# `waypoint-react-nondeterministic-render`

> Beacon schema — generated from `infra/react/edge-case/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> Math.random()/new Date()/Date.now() in render body — impure render, hydration mismatch, unstable ids?

## Where the detection code lives
- **Rule:** [`infra/react/edge-case/react-hardening.yaml`](../../../infra/react/edge-case/react-hardening.yaml) — Semgrep rule `waypoint-react-nondeterministic-render`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-nondeterministic-render`
- **Also flagged by (when that tool is installed):** bandit `B311` (random); ruff `S311`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-nondeterministic-render", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "Math.random()/new Date()/Date.now() in render body — impure render, hydration mismatch, unstable ids?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-nondeterministic-render" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
  // WAYPOINT-PLANT: waypoint-react-nondeterministic-render [axes: edge-case]
  const id = Math.random();
  // WAYPOINT-PLANT: waypoint-react-nondeterministic-render [axes: edge-case]
```
