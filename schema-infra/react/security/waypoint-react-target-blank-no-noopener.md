# `waypoint-react-target-blank-no-noopener`

> Beacon schema — generated from `infra/react/security/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> target=_blank link missing rel=noopener — reverse tabnabbing?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening.yaml`](../../../infra/react/security/react-hardening.yaml) — Semgrep rule `waypoint-react-target-blank-no-noopener`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-target-blank-no-noopener`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-target-blank-no-noopener", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "target=_blank link missing rel=noopener — reverse tabnabbing?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-target-blank-no-noopener" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-target-blank-no-noopener [axes: security] */}
      <a href={url} target="_blank">
        external
```
