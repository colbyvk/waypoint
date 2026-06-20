# `waypoint-py-logic-eq-none`

> Beacon schema — generated from `infra/python/logic/python-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** logic
- **Language(s):** python

## Agent hypothesis
> `== None` / `!= None` instead of `is None` — a custom __eq__ could make this check lie?

## Where the detection code lives
- **Rule:** [`infra/python/logic/python-logic.yaml`](../../../infra/python/logic/python-logic.yaml) — Semgrep rule `waypoint-py-logic-eq-none`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-logic-eq-none`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-logic-eq-none", "level": "note",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.3,
    "hypothesis": "`== None` / `!= None` instead of `is None` — a custom __eq__ could make this check lie?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-logic-eq-none" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/logic_samples.py
    # WAYPOINT-PLANT: waypoint-py-logic-eq-none
    if x == None:
        return 1
```
