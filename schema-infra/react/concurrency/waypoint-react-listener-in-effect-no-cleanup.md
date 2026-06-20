# `waypoint-react-listener-in-effect-no-cleanup`

> Beacon schema — generated from `infra/react/concurrency/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, edge-case
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> addEventListener/subscribe in useEffect with no removeEventListener/unsubscribe cleanup — leaked handler firing after unmount?

## Where the detection code lives
- **Rule:** [`infra/react/concurrency/react-hardening.yaml`](../../../infra/react/concurrency/react-hardening.yaml) — Semgrep rule `waypoint-react-listener-in-effect-no-cleanup`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-listener-in-effect-no-cleanup`
- **Also flagged by (when that tool is installed):** eslint `react-hooks/exhaustive-deps`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-listener-in-effect-no-cleanup", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "edge-case"], "severity_prior": 0.6,
    "hypothesis": "addEventListener/subscribe in useEffect with no removeEventListener/unsubscribe cleanup — leaked handler firing after unmount?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-listener-in-effect-no-cleanup" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
  // WAYPOINT-PLANT: waypoint-react-listener-in-effect-no-cleanup [axes: concurrency,edge-case]
  useEffect(() => {
    window.addEventListener("resize", () => setW(window.innerWidth));
```
