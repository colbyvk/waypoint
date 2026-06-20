# `waypoint-react-process-env-in-client`

> Beacon schema — generated from `infra/react/security/react-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> process.env.X inside a client component — secret inlined into the JS bundle?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening2.yaml`](../../../infra/react/security/react-hardening2.yaml) — Semgrep rule `waypoint-react-process-env-in-client`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-process-env-in-client`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-process-env-in-client", "level": "note",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.3,
    "hypothesis": "process.env.X inside a client component — secret inlined into the JS bundle?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-process-env-in-client" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/Hardening2.tsx
  // WAYPOINT-PLANT: waypoint-react-process-env-in-client
  const key = process.env.STRIPE_SECRET_KEY;
  // WAYPOINT-OK: public, non-secret config is fine to inline
```
