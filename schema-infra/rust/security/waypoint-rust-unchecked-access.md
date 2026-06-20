# `waypoint-rust-unchecked-access`

> Beacon schema — generated from `infra/rust/security/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, edge-case
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> unchecked get/from_utf8 — can an out-of-bounds index or invalid UTF-8 reach this (UB)?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening.yaml`](../../../infra/rust/security/rust-hardening.yaml) — Semgrep rule `waypoint-rust-unchecked-access`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-unchecked-access`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-unchecked-access", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "edge-case"], "severity_prior": 0.9,
    "hypothesis": "unchecked get/from_utf8 — can an out-of-bounds index or invalid UTF-8 reach this (UB)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-unchecked-access" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-unchecked-access
    unsafe { *buf.get_unchecked(i) }
}
```
