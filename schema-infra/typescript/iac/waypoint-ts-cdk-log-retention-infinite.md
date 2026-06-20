# `waypoint-ts-cdk-log-retention-infinite`

> Beacon schema — generated from `infra/typescript/iac/typescript-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** iac
- **Language(s):** typescript

## Agent hypothesis
> LogGroup with no retention: prop — logs kept forever / no defined window?

## Where the detection code lives
- **Rule:** [`infra/typescript/iac/typescript-cdk.yaml`](../../../infra/typescript/iac/typescript-cdk.yaml) — Semgrep rule `waypoint-ts-cdk-log-retention-infinite`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-cdk-log-retention-infinite`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-cdk-log-retention-infinite", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "LogGroup with no retention: prop — logs kept forever / no defined window?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-cdk-log-retention-infinite" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/cdkStack.ts
    // WAYPOINT-PLANT: waypoint-ts-cdk-log-retention-infinite
    // WAYPOINT-PLANT: waypoint-ts-cdk-destructive-removal-policy
    const auditLogs = new logs.LogGroup(this, "AuditLogs", {
```
