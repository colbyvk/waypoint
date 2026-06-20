# `waypoint-py-sql-string-build`

> Beacon schema — generated from `infra/python/security/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> string-built SQL into execute() — injection if input is untrusted?

## Where the detection code lives
- **Rule:** [`infra/python/security/python.yaml`](../../../infra/python/security/python.yaml) — Semgrep rule `waypoint-py-sql-string-build`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-sql-string-build`
- **Also flagged by (when that tool is installed):** bandit `B608` (SQL injection); ruff `S608` (hardcoded-sql)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-sql-string-build", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.9,
    "hypothesis": "string-built SQL into execute() — injection if input is untrusted?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-sql-string-build" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/sql-string-build.md`](../../../hazards/sql-string-build.md)
