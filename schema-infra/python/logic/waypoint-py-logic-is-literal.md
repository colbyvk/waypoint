# `waypoint-py-logic-is-literal`

> Beacon schema — generated from `infra/python/logic/python-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** python

## Agent hypothesis
> identity check against a literal ($X is <int/str>) — value comparison (==) almost certainly meant?

## Where the detection code lives
- **Rule:** [`infra/python/logic/python-logic.yaml`](../../../infra/python/logic/python-logic.yaml) — Semgrep rule `waypoint-py-logic-is-literal`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-logic-is-literal`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-logic-is-literal", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "identity check against a literal ($X is <int/str>) — value comparison (==) almost certainly meant?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-logic-is-literal" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/logic_samples.py
    # WAYPOINT-PLANT: waypoint-py-logic-is-literal
    if x is 5:
        return 1
```
