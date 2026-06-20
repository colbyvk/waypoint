# `waypoint-rust-lock-across-await`

> Beacon schema — generated from `infra/rust/concurrency/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> lock().unwrap()/lock().await inside async fn with awaits — is a guard held across an await point (deadlock)?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust-hardening.yaml`](../../../infra/rust/concurrency/rust-hardening.yaml) — Semgrep rule `waypoint-rust-lock-across-await`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-lock-across-await`
- **Also flagged by (when that tool is installed):** clippy `clippy::unwrap_used`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-lock-across-await", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.6,
    "hypothesis": "lock().unwrap()/lock().await inside async fn with awaits — is a guard held across an await point (deadlock)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-lock-across-await" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-lock-across-await
    let mut g = m.lock().unwrap();
    *g += 1;
```
