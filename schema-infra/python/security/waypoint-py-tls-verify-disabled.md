# `waypoint-py-tls-verify-disabled`

> Beacon schema — generated from `infra/python/security/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> verify=False / unverified TLS context — MITM exposure?

## Where the detection code lives
- **Rule:** [`infra/python/security/python.yaml`](../../../infra/python/security/python.yaml) — Semgrep rule `waypoint-py-tls-verify-disabled`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-tls-verify-disabled`
- **Also flagged by (when that tool is installed):** bandit `B501` (request_with_no_cert_validation); ruff `S501`; bandit `B501`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-tls-verify-disabled", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "verify=False / unverified TLS context — MITM exposure?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-tls-verify-disabled" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
