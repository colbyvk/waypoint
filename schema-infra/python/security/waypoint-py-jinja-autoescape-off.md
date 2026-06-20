# `waypoint-py-jinja-autoescape-off`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> jinja2 Environment(autoescape=False) — XSS on rendered user content?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-jinja-autoescape-off`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-jinja-autoescape-off`
- **Also flagged by (when that tool is installed):** eslint `security/*`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-jinja-autoescape-off", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "jinja2 Environment(autoescape=False) — XSS on rendered user content?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-jinja-autoescape-off" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-jinja-autoescape-off
    return Environment(autoescape=False)

```
