# `waypoint-rust-panic-family`

> Beacon schema — generated from `infra/rust/edge-case/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** rust

## Agent hypothesis
> expect/unreachable/todo/unimplemented/panic — reachable on a real input (DoS)?

## Where the detection code lives
- **Rule:** [`infra/rust/edge-case/rust-hardening.yaml`](../../../infra/rust/edge-case/rust-hardening.yaml) — Semgrep rule `waypoint-rust-panic-family`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-panic-family`
- **Also flagged by (when that tool is installed):** clippy `clippy::panic` / `clippy::unwrap_used`; clippy `clippy::expect_used`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-panic-family", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "expect/unreachable/todo/unimplemented/panic — reachable on a real input (DoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-panic-family" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-panic-family
    raw.expect("config must be present")
}
```
