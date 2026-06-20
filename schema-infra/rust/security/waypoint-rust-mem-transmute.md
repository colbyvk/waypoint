# `waypoint-rust-mem-transmute`

> Beacon schema — generated from `infra/rust/security/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> mem::transmute — could it produce an invalid value or break layout assumptions?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening.yaml`](../../../infra/rust/security/rust-hardening.yaml) — Semgrep rule `waypoint-rust-mem-transmute`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-mem-transmute`
- **Also flagged by (when that tool is installed):** clippy `clippy::transmute_*`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-mem-transmute", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "mem::transmute — could it produce an invalid value or break layout assumptions?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-mem-transmute" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-mem-transmute
    unsafe { mem::transmute(x) }
}
```
