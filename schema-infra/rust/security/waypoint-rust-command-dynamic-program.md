# `waypoint-rust-command-dynamic-program`

> Beacon schema — generated from `infra/rust/security/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> Command::new(variable) — is the executed program name attacker-controlled?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening.yaml`](../../../infra/rust/security/rust-hardening.yaml) — Semgrep rule `waypoint-rust-command-dynamic-program`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-command-dynamic-program`
- **Also flagged by (when that tool is installed):** eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-command-dynamic-program", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.6,
    "hypothesis": "Command::new(variable) — is the executed program name attacker-controlled?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-command-dynamic-program" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-command-dynamic-program
    Command::new(program).arg("--version").output()
}
```
