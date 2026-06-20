# `waypoint-py-subprocess-shell`

> Beacon schema — generated from `infra/python/security/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> shell=True / os.system — command injection if argument is untrusted?

## Where the detection code lives
- **Rule:** [`infra/python/security/python.yaml`](../../../infra/python/security/python.yaml) — Semgrep rule `waypoint-py-subprocess-shell`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-subprocess-shell`
- **Also flagged by (when that tool is installed):** bandit `B602`–`B607`; ruff `S602`–`S607`; bandit `B605` (start_process_with_a_shell); eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-subprocess-shell", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "shell=True / os.system — command injection if argument is untrusted?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-subprocess-shell" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
