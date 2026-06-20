# `waypoint-py-idor-lookup-by-id`

> Beacon schema — generated from `infra/python/abuse/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** python

## Agent hypothesis
> lookup by user-supplied id — missing ownership/authorization check (IDOR)?

## Where the detection code lives
- **Rule:** [`infra/python/abuse/python.yaml`](../../../infra/python/abuse/python.yaml) — Semgrep rule `waypoint-py-idor-lookup-by-id`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-idor-lookup-by-id`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-idor-lookup-by-id", "level": "note",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.3,
    "hypothesis": "lookup by user-supplied id — missing ownership/authorization check (IDOR)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-idor-lookup-by-id" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
