# `waypoint-react-unsafe-href`

> Beacon schema — generated from `infra/react/security/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> href/src bound to a dynamic value — javascript: URI, data: URI, or open redirect?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening.yaml`](../../../infra/react/security/react-hardening.yaml) — Semgrep rule `waypoint-react-unsafe-href`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-unsafe-href`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-unsafe-href", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "href/src bound to a dynamic value — javascript: URI, data: URI, or open redirect?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-unsafe-href" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-unsafe-href [axes: security] */}
      <a href={url}>profile</a>

```
