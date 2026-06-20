# `waypoint-py-authz-privilege-from-request`

> Beacon schema — generated from `infra/python/authz/python-authz.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> privilege field (is_admin/role/permissions/…) set from request input — privilege escalation?

## Where the detection code lives
- **Rule:** [`infra/python/authz/python-authz.yaml`](../../../infra/python/authz/python-authz.yaml) — Semgrep rule `waypoint-py-authz-privilege-from-request`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-authz-privilege-from-request`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-authz-privilege-from-request", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.9,
    "hypothesis": "privilege field (is_admin/role/permissions/…) set from request input — privilege escalation?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-authz-privilege-from-request" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/authz_samples.py
    # WAYPOINT-PLANT: waypoint-py-authz-privilege-from-request
    user.is_admin = request.json["is_admin"]
    return user
```
