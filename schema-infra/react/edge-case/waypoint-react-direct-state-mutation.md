# `waypoint-react-direct-state-mutation`

> Beacon schema — generated from `infra/react/edge-case/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** typescript

## Agent hypothesis
> in-place mutation of suspected React state (push/splice/field=) — stale UI / skipped re-render?

## Where the detection code lives
- **Rule:** [`infra/react/edge-case/react-hardening.yaml`](../../../infra/react/edge-case/react-hardening.yaml) — Semgrep rule `waypoint-react-direct-state-mutation`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-direct-state-mutation`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-direct-state-mutation", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "in-place mutation of suspected React state (push/splice/field=) — stale UI / skipped re-render?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-direct-state-mutation" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
    // WAYPOINT-PLANT: waypoint-react-direct-state-mutation [axes: edge-case]
    list.push(x);
    // WAYPOINT-PLANT: waypoint-react-direct-state-mutation [axes: edge-case]
```
