# `waypoint-py-logic-return-in-finally`

> Beacon schema — generated from `infra/python/logic/python-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** python

## Agent hypothesis
> control flow (return/break/continue) inside finally — silently discards exceptions or the real return value?

## Where the detection code lives
- **Rule:** [`infra/python/logic/python-logic.yaml`](../../../infra/python/logic/python-logic.yaml) — Semgrep rule `waypoint-py-logic-return-in-finally`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-logic-return-in-finally`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-logic-return-in-finally", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "control flow (return/break/continue) inside finally — silently discards exceptions or the real return value?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-logic-return-in-finally" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/logic_samples.py
        # WAYPOINT-PLANT: waypoint-py-logic-return-in-finally
        return 0

```
