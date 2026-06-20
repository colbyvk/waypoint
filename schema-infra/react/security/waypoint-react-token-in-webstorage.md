# `waypoint-react-token-in-webstorage`

> Beacon schema — generated from `infra/react/security/react-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> auth token/secret in localStorage/sessionStorage — exfiltratable by any XSS on the origin?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening2.yaml`](../../../infra/react/security/react-hardening2.yaml) — Semgrep rule `waypoint-react-token-in-webstorage`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-token-in-webstorage`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret); eslint `security/*`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-token-in-webstorage", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "auth token/secret in localStorage/sessionStorage — exfiltratable by any XSS on the origin?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-token-in-webstorage" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/Hardening2.tsx
    // WAYPOINT-PLANT: waypoint-react-token-in-webstorage
    localStorage.setItem("auth_token", token);
  }
```
