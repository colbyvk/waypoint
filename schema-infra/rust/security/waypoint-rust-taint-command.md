# `waypoint-rust-taint-command`

> Beacon schema — generated from `infra/rust/security/rust-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> tainted env/args reaches a Command argument — command injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-taint.yaml`](../../../infra/rust/security/rust-taint.yaml) — Semgrep rule `waypoint-rust-taint-command`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-taint-command`
- **Also flagged by (when that tool is installed):** eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-taint-command", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "tainted env/args reaches a Command argument — command injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-taint-command" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/taint_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-taint-command
    Command::new("sh").arg("-c").arg(host);
    // WAYPOINT-OK: constant argument
```
