# `waypoint-py-path-traversal`

> Beacon schema — generated from `infra/python/security/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> open(join(base, user)) with no containment check — path traversal?

## Where the detection code lives
- **Rule:** [`infra/python/security/python.yaml`](../../../infra/python/security/python.yaml) — Semgrep rule `waypoint-py-path-traversal`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-path-traversal`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-path-traversal", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "open(join(base, user)) with no containment check — path traversal?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-path-traversal" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
