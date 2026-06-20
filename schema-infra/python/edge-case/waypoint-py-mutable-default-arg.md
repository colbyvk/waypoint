# `waypoint-py-mutable-default-arg`

> Beacon schema — generated from `infra/python/edge-case/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** edge-case
- **Language(s):** python

## Agent hypothesis
> mutable default arg ([]/{}/dict()/list()/set()) — state leaking across calls if mutated?

## Where the detection code lives
- **Rule:** [`infra/python/edge-case/python-hardening.yaml`](../../../infra/python/edge-case/python-hardening.yaml) — Semgrep rule `waypoint-py-mutable-default-arg`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-mutable-default-arg`
- **Also flagged by (when that tool is installed):** ruff `B006`; bandit (n/a)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-mutable-default-arg", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.6,
    "hypothesis": "mutable default arg ([]/{}/dict()/list()/set()) — state leaking across calls if mutated?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-mutable-default-arg" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
# WAYPOINT-PLANT: waypoint-py-mutable-default-arg
def add_item(item, bucket=[]):
    bucket.append(item)
```
