# `waypoint-py-unsafe-deser`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> pickle/marshal load of untrusted bytes — RCE on deserialization?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-unsafe-deser`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-unsafe-deser`
- **Also flagged by (when that tool is installed):** bandit `B301`/`B302` (pickle)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-unsafe-deser", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "pickle/marshal load of untrusted bytes — RCE on deserialization?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-unsafe-deser" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-unsafe-deser
    return pickle.loads(blob)

```
