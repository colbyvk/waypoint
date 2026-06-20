# `waypoint-ts-insecure-cookie`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> res.cookie / cookie.serialize without httpOnly+secure+sameSite — session/auth cookie exposed?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening2.yaml`](../../../infra/typescript/security/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-insecure-cookie`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-insecure-cookie`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-insecure-cookie", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "res.cookie / cookie.serialize without httpOnly+secure+sameSite — session/auth cookie exposed?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-insecure-cookie" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-insecure-cookie
  res.cookie("session", token);
}
```
