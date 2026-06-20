# `waypoint-py-open-without-with`

> Beacon schema — generated from `infra/python/edge-case/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> open() outside a with-block — descriptor leak if close() is skipped on error?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening.yaml`](../../../infra/python/edge-case/python-hardening.yaml) — Semgrep rule `waypoint-py-open-without-with`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-open-without-with`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-open-without-with", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "open() outside a with-block — descriptor leak if close() is skipped on error?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-open-without-with" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-open-without-with
    f = open(path)
    data = f.read()
```
