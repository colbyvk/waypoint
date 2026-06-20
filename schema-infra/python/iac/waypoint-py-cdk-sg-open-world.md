# `waypoint-py-cdk-sg-open-world`

> Beacon schema — generated from `infra/python/iac/python-cdk.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** iac
- **Language(s):** python

## Agent hypothesis
> security group ingress from Peer.any_ipv4/any_ipv6 — open to the world?

## Where the detection code lives
- **Rule:** [`infra/python/iac/python-cdk.yaml`](../../../infra/python/iac/python-cdk.yaml) — Semgrep rule `waypoint-py-cdk-sg-open-world`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-cdk-sg-open-world`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-cdk-sg-open-world", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "security group ingress from Peer.any_ipv4/any_ipv6 — open to the world?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-cdk-sg-open-world" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/cdk_stack.py
        # WAYPOINT-PLANT: waypoint-py-cdk-sg-open-world
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "ssh world")

```
