# `waypoint-py-flask-cors-wildcard`

> Beacon schema — generated from `infra/python/security/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> Flask-CORS origins="*" — any origin can call authenticated endpoints (CORS bypass)?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening2.yaml`](../../../infra/python/security/python-hardening2.yaml) — Semgrep rule `waypoint-py-flask-cors-wildcard`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-flask-cors-wildcard`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-flask-cors-wildcard", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "Flask-CORS origins="*" — any origin can call authenticated endpoints (CORS bypass)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-flask-cors-wildcard" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-flask-cors-wildcard
    return CORS(application, origins="*")

```
