# `waypoint-py-toctou-exists-open`

> Beacon schema — generated from `infra/python/edge-case/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case, security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> os.path.exists/isfile($P) then open($P) — file swapped between check and use (TOCTOU)?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening2.yaml`](../../../infra/python/edge-case/python-hardening2.yaml) — Semgrep rule `waypoint-py-toctou-exists-open`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-toctou-exists-open`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-toctou-exists-open", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["edge-case", "security"], "severity_prior": 0.6,
    "hypothesis": "os.path.exists/isfile($P) then open($P) — file swapped between check and use (TOCTOU)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-toctou-exists-open" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-toctou-exists-open
    if os.path.exists(path):
        f = open(path)
```
