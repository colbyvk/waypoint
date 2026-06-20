# `waypoint-py-request-no-timeout`

> Beacon schema — generated from `infra/python/edge-case/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> requests.* without timeout= — indefinite hang / resource exhaustion on a slow peer?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening.yaml`](../../../infra/python/edge-case/python-hardening.yaml) — Semgrep rule `waypoint-py-request-no-timeout`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-request-no-timeout`
- **Also flagged by (when that tool is installed):** bandit `B113` (request_without_timeout)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-request-no-timeout", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["edge-case", "abuse"], "severity_prior": 0.6,
    "hypothesis": "requests.* without timeout= — indefinite hang / resource exhaustion on a slow peer?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-request-no-timeout" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-request-no-timeout
    return requests.get(url)

```
