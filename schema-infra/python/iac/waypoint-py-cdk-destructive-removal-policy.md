# `waypoint-py-cdk-destructive-removal-policy`

> Beacon schema — generated from `infra/python/iac/python-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** iac
- **Language(s):** python

## Agent hypothesis
> removal_policy=RemovalPolicy.DESTROY on a data store — data lost on stack delete?

## Where the detection code lives
- **Rule:** [`infra/python/iac/python-cdk.yaml`](../../../infra/python/iac/python-cdk.yaml) — Semgrep rule `waypoint-py-cdk-destructive-removal-policy`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-cdk-destructive-removal-policy`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-cdk-destructive-removal-policy", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "removal_policy=RemovalPolicy.DESTROY on a data store — data lost on stack delete?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-cdk-destructive-removal-policy" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/cdk_stack.py
        # WAYPOINT-PLANT: waypoint-py-cdk-destructive-removal-policy
        scratch_bucket = s3.Bucket(
            self,
```
