# `waypoint-py-yaml-unsafe-load`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> yaml.load without SafeLoader on untrusted input — object injection / RCE?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-yaml-unsafe-load`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-yaml-unsafe-load`
- **Also flagged by (when that tool is installed):** bandit `B506` (yaml_load)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-yaml-unsafe-load", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "yaml.load without SafeLoader on untrusted input — object injection / RCE?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-yaml-unsafe-load" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-yaml-unsafe-load
    return yaml.load(text)

```
