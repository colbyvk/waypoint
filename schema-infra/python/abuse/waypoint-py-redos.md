# `waypoint-py-redos`

> Beacon schema — generated from `infra/python/abuse/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse, security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** abuse
- **Language(s):** python

## Agent hypothesis
> regex with nested quantifiers on input — catastrophic backtracking (ReDoS)?

## Where the detection code lives
- **Rule:** [`infra/python/abuse/python.yaml`](../../../infra/python/abuse/python.yaml) — Semgrep rule `waypoint-py-redos`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-redos`
- **Also flagged by (when that tool is installed):** eslint `security/detect-unsafe-regex`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-redos", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["abuse", "security"], "severity_prior": 0.6,
    "hypothesis": "regex with nested quantifiers on input — catastrophic backtracking (ReDoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-redos" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/redos.md`](../../../hazards/redos.md)
