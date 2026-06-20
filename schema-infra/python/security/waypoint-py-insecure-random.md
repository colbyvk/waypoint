# `waypoint-py-insecure-random`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> random.* output used as a token/secret/nonce — predictable, should be secrets/os.urandom?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-insecure-random`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-insecure-random`
- **Also flagged by (when that tool is installed):** gitleaks (secret scan); bandit `B105`–`B107`; trivy (secret); bandit `B311` (random); ruff `S311`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-insecure-random", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "random.* output used as a token/secret/nonce — predictable, should be secrets/os.urandom?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-insecure-random" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-insecure-random
    return random.randint(0, 999999)

```
