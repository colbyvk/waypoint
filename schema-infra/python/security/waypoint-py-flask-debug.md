# `waypoint-py-flask-debug`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> app.run(debug=True) — interactive debugger / RCE exposed in a reachable deploy?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-flask-debug`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-flask-debug`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-flask-debug", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "app.run(debug=True) — interactive debugger / RCE exposed in a reachable deploy?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-flask-debug" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-flask-debug
    app.run(host="0.0.0.0", debug=True)

```
