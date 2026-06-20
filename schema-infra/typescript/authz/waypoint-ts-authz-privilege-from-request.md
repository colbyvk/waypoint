# `waypoint-ts-authz-privilege-from-request`

> Beacon schema — generated from `infra/typescript/authz/typescript-authz.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> privilege field (isAdmin/role/permissions/…) set from req input — privilege escalation?

## Where the detection code lives
- **Rule:** [`infra/typescript/authz/typescript-authz.yaml`](../../../infra/typescript/authz/typescript-authz.yaml) — Semgrep rule `waypoint-ts-authz-privilege-from-request`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-authz-privilege-from-request`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-authz-privilege-from-request", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.9,
    "hypothesis": "privilege field (isAdmin/role/permissions/…) set from req input — privilege escalation?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-authz-privilege-from-request" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/authz_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-authz-privilege-from-request
  user.isAdmin = req.body.isAdmin;
  return user;
```
