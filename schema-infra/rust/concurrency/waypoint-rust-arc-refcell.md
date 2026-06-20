# `waypoint-rust-arc-refcell`

> Beacon schema — generated from `infra/rust/concurrency/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> Arc<RefCell<...>> — non-thread-safe interior mutability shared across threads (data race / panic)?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust-hardening2.yaml`](../../../infra/rust/concurrency/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-arc-refcell`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-arc-refcell`
- **Also flagged by (when that tool is installed):** clippy `clippy::panic` / `clippy::unwrap_used`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-arc-refcell", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.6,
    "hypothesis": "Arc<RefCell<...>> — non-thread-safe interior mutability shared across threads (data race / panic)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-arc-refcell" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-arc-refcell
    Arc::new(RefCell::new(0))
}
```
