# `waypoint-py-assert-validation`

> Beacon schema — generated from `infra/python/edge-case/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case, security
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> assert as a validation gate — bypassed under -O, leaving the check unenforced?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening.yaml`](../../../infra/python/edge-case/python-hardening.yaml) — Semgrep rule `waypoint-py-assert-validation`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-assert-validation`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-assert-validation", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case", "security"], "severity_prior": 0.3,
    "hypothesis": "assert as a validation gate — bypassed under -O, leaving the check unenforced?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-assert-validation" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-assert-validation
    assert amount > 0
    return amount
```
