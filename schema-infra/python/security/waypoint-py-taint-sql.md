# `waypoint-py-taint-sql`

> Beacon schema — generated from `infra/python/security/python-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> tainted input reaches a SQL query unsanitized — injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-taint.yaml`](../../../infra/python/security/python-taint.yaml) — Semgrep rule `waypoint-py-taint-sql`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-taint-sql`
- **Also flagged by (when that tool is installed):** bandit `B608` (SQL injection); ruff `S608` (hardcoded-sql)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-taint-sql", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.9,
    "hypothesis": "tainted input reaches a SQL query unsanitized — injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-taint-sql" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/taint_samples.py
    # WAYPOINT-PLANT: waypoint-py-taint-sql
    cur.execute("SELECT * FROM users WHERE name = '" + name + "'")
    # WAYPOINT-OK: parametrized — the query string is a constant, input is bound
```
