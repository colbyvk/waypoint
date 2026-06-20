# `waypoint-ts-authz-mass-assignment`

> Beacon schema — generated from `infra/typescript/authz/typescript-authz.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> untrusted req.body bulk-assigned into a model/ORM write — mass assignment / privilege escalation?

## Where the detection code lives
- **Rule:** [`infra/typescript/authz/typescript-authz.yaml`](../../../infra/typescript/authz/typescript-authz.yaml) — Semgrep rule `waypoint-ts-authz-mass-assignment`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-authz-mass-assignment`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-authz-mass-assignment", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "untrusted req.body bulk-assigned into a model/ORM write — mass assignment / privilege escalation?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-authz-mass-assignment" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/authz_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-authz-mass-assignment
  Object.assign(user, req.body);
  return user;
```
