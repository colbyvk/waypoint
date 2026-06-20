# `waypoint-py-hardcoded-secret`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> secret-named variable assigned a string literal — hardcoded credential in source?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-hardcoded-secret`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-hardcoded-secret`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-hardcoded-secret", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "secret-named variable assigned a string literal — hardcoded credential in source?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-hardcoded-secret" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
# WAYPOINT-PLANT: waypoint-py-hardcoded-secret
API_KEY = "EXAMPLE-not-a-real-stripe-key"
# WAYPOINT-PLANT: waypoint-py-hardcoded-secret
```
