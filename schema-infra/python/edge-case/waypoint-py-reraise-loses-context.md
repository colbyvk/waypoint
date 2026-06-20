# `waypoint-py-reraise-loses-context`

> Beacon schema — generated from `infra/python/edge-case/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> except raises a different error with no `from` — original cause/traceback lost?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening2.yaml`](../../../infra/python/edge-case/python-hardening2.yaml) — Semgrep rule `waypoint-py-reraise-loses-context`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-reraise-loses-context`
- **Also flagged by (when that tool is installed):** ruff `E722` (bare-except), `S110`, `BLE001` (blind-except)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-reraise-loses-context", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "except raises a different error with no `from` — original cause/traceback lost?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-reraise-loses-context" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-reraise-loses-context
    try:
        return int(text)
```
