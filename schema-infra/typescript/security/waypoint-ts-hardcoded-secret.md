# `waypoint-ts-hardcoded-secret`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> credential-named var assigned a string literal — hardcoded secret?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening.yaml`](../../../infra/typescript/security/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-hardcoded-secret`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-hardcoded-secret`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-hardcoded-secret", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "credential-named var assigned a string literal — hardcoded secret?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-hardcoded-secret" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
// WAYPOINT-PLANT: waypoint-ts-hardcoded-secret
const password = "hunter2";
// WAYPOINT-PLANT: waypoint-ts-hardcoded-secret
```
