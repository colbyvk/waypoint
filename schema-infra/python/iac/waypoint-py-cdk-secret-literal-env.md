# `waypoint-py-cdk-secret-literal-env`

> Beacon schema — generated from `infra/python/iac/python-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** iac
- **Language(s):** python

## Agent hypothesis
> environment={...PASSWORD/SECRET/TOKEN...: '<literal>'} — hard-coded credential in IaC?

## Where the detection code lives
- **Rule:** [`infra/python/iac/python-cdk.yaml`](../../../infra/python/iac/python-cdk.yaml) — Semgrep rule `waypoint-py-cdk-secret-literal-env`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-cdk-secret-literal-env`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-cdk-secret-literal-env", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "environment={...PASSWORD/SECRET/TOKEN...: '<literal>'} — hard-coded credential in IaC?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-cdk-secret-literal-env" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/cdk_stack.py
        # WAYPOINT-PLANT: waypoint-py-cdk-secret-literal-env
        task_def = ecs.FargateTaskDefinition(self, "Task")
        task_def.add_container(
```
