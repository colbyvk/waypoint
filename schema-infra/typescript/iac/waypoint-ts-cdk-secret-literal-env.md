# `waypoint-ts-cdk-secret-literal-env`

> Beacon schema — generated from `infra/typescript/iac/typescript-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** iac
- **Language(s):** typescript

## Agent hypothesis
> environment={ ...PASSWORD/SECRET/TOKEN...: '<literal>' } — hard-coded credential in IaC?

## Where the detection code lives
- **Rule:** [`infra/typescript/iac/typescript-cdk.yaml`](../../../infra/typescript/iac/typescript-cdk.yaml) — Semgrep rule `waypoint-ts-cdk-secret-literal-env`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-cdk-secret-literal-env`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-cdk-secret-literal-env", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "environment={ ...PASSWORD/SECRET/TOKEN...: '<literal>' } — hard-coded credential in IaC?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-cdk-secret-literal-env" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/cdkStack.ts
    // WAYPOINT-PLANT: waypoint-ts-cdk-secret-literal-env
    const taskDef = new ecs.FargateTaskDefinition(this, "Task");
    taskDef.addContainer("app", {
```
