# `waypoint-py-authz-route-no-auth`

> Beacon schema — generated from `infra/python/authz/python-authz.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> route handler has no auth decorator (@login_required/@jwt_required/…) — unauthenticated endpoint?

## Where the detection code lives
- **Rule:** [`infra/python/authz/python-authz.yaml`](../../../infra/python/authz/python-authz.yaml) — Semgrep rule `waypoint-py-authz-route-no-auth`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-authz-route-no-auth`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-authz-route-no-auth", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "route handler has no auth decorator (@login_required/@jwt_required/…) — unauthenticated endpoint?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-authz-route-no-auth" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/authz_samples.py
    # WAYPOINT-PLANT: waypoint-py-authz-route-no-auth (no auth decorator)
    return "deleted"

```
