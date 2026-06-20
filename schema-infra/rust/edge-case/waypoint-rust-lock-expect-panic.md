# `waypoint-rust-lock-expect-panic`

> Beacon schema — generated from `infra/rust/edge-case/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case, concurrency
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** edge-case
- **Language(s):** rust

## Agent hypothesis
> lock().expect()/unwrap() — poisoned lock turns one panic into a cascading crash?

## Where the detection code lives
- **Rule:** [`infra/rust/edge-case/rust-hardening2.yaml`](../../../infra/rust/edge-case/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-lock-expect-panic`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-lock-expect-panic`
- **Also flagged by (when that tool is installed):** clippy `clippy::unwrap_used`; clippy `clippy::panic` / `clippy::unwrap_used`; clippy `clippy::expect_used`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-lock-expect-panic", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["edge-case", "concurrency"], "severity_prior": 0.6,
    "hypothesis": "lock().expect()/unwrap() — poisoned lock turns one panic into a cascading crash?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-lock-expect-panic" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-lock-expect-panic
    *m.lock().expect("lock poisoned")
}
```
