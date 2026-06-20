# `waypoint-py-taint-ssrf`

> Beacon schema — generated from `infra/python/security/python-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> tainted input reaches an HTTP-client URL — SSRF along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-taint.yaml`](../../../infra/python/security/python-taint.yaml) — Semgrep rule `waypoint-py-taint-ssrf`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-taint-ssrf`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-taint-ssrf", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "tainted input reaches an HTTP-client URL — SSRF along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-taint-ssrf" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/taint_samples.py
    # WAYPOINT-PLANT: waypoint-py-taint-ssrf
    requests.get(url)
    # WAYPOINT-OK: constant, internal URL
```
