# `waypoint-py-unbounded-read`

> Beacon schema — generated from `infra/python/abuse/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** python

## Agent hypothesis
> read() with no size limit on an input stream — unbounded memory allocation / DoS?

## Where the detection code lives
- **Rule:** [`infra/python/abuse/python-hardening.yaml`](../../../infra/python/abuse/python-hardening.yaml) — Semgrep rule `waypoint-py-unbounded-read`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-unbounded-read`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-unbounded-read", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "read() with no size limit on an input stream — unbounded memory allocation / DoS?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-unbounded-read" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-unbounded-read
    return resp.read()

```
