# `waypoint-ts-cdk-s3-public`

> Beacon schema — generated from `infra/typescript/iac/typescript-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** iac
- **Language(s):** typescript

## Agent hypothesis
> S3 bucket with publicReadAccess:true / disabled BPA — intended public exposure?

## Where the detection code lives
- **Rule:** [`infra/typescript/iac/typescript-cdk.yaml`](../../../infra/typescript/iac/typescript-cdk.yaml) — Semgrep rule `waypoint-ts-cdk-s3-public`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-cdk-s3-public`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-cdk-s3-public", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "S3 bucket with publicReadAccess:true / disabled BPA — intended public exposure?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-cdk-s3-public" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/cdkStack.ts
    // WAYPOINT-PLANT: waypoint-ts-cdk-s3-public
    const publicBucket = new s3.Bucket(this, "PublicBucket", {
      publicReadAccess: true,
```
