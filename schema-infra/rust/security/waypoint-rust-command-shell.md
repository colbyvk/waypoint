# `waypoint-rust-command-shell`

> Beacon schema — generated from `infra/rust/security/rust.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> Command::new("sh"/"bash") — interpolated arg leading to command injection?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust.yaml`](../../../infra/rust/security/rust.yaml) — Semgrep rule `waypoint-rust-command-shell`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-command-shell`
- **Also flagged by (when that tool is installed):** bandit `B605` (start_process_with_a_shell); eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-command-shell", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "Command::new("sh"/"bash") — interpolated arg leading to command injection?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-command-shell" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
