# `waypoint-py-django-raw-sql`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> Django .raw/.extra/RawSQL — unparametrized user input reaching the query (SQLi)?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-django-raw-sql`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-django-raw-sql`
- **Also flagged by (when that tool is installed):** bandit `B608` (SQL injection); ruff `S608` (hardcoded-sql)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-django-raw-sql", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "Django .raw/.extra/RawSQL — unparametrized user input reaching the query (SQLi)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-django-raw-sql" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-django-raw-sql
    return model.objects.raw("SELECT * FROM t WHERE name = '%s'" % term)

```
