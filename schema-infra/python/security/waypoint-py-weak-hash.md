# `waypoint-py-weak-hash`

> Beacon schema — generated from `infra/python/security/python-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> md5/sha1 — used in a security-sensitive context (collisions/preimage)?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening.yaml`](../../../infra/python/security/python-hardening.yaml) — Semgrep rule `waypoint-py-weak-hash`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-weak-hash`
- **Also flagged by (when that tool is installed):** bandit `B303`/`B324` (weak hash)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-weak-hash", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "md5/sha1 — used in a security-sensitive context (collisions/preimage)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-weak-hash" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening_samples.py
    # WAYPOINT-PLANT: waypoint-py-weak-hash
    return hashlib.md5(data).hexdigest()

```
