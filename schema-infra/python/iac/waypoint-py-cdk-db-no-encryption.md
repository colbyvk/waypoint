# `waypoint-py-cdk-db-no-encryption`

> Beacon schema — generated from `infra/python/iac/python-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** iac
- **Language(s):** python

## Agent hypothesis
> RDS/Redshift built with no storage_encrypted=True — unencrypted DB at rest?

## Where the detection code lives
- **Rule:** [`infra/python/iac/python-cdk.yaml`](../../../infra/python/iac/python-cdk.yaml) — Semgrep rule `waypoint-py-cdk-db-no-encryption`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-cdk-db-no-encryption`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-cdk-db-no-encryption", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "RDS/Redshift built with no storage_encrypted=True — unencrypted DB at rest?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-cdk-db-no-encryption" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/cdk_stack.py
        # WAYPOINT-PLANT: waypoint-py-cdk-db-no-encryption
        # WAYPOINT-PLANT: waypoint-py-cdk-db-public
        analytics_db = rds.DatabaseInstance(
```
