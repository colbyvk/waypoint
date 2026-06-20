# `waypoint-react-insecure-http-url`

> Beacon schema — generated from `infra/react/security/react-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> plain http:// URL in fetch/href/src — cleartext transport (MITM / mixed content)?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening2.yaml`](../../../infra/react/security/react-hardening2.yaml) — Semgrep rule `waypoint-react-insecure-http-url`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-insecure-http-url`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-insecure-http-url", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "plain http:// URL in fetch/href/src — cleartext transport (MITM / mixed content)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-insecure-http-url" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/Hardening2.tsx
    // WAYPOINT-PLANT: waypoint-react-insecure-http-url
    return fetch("http://api.example.com/feed");
  }
```
