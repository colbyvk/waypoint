# `waypoint-rust-panicking-index`

> Beacon schema — generated from `infra/rust/edge-case/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** edge-case
- **Language(s):** rust

## Agent hypothesis
> slice/Vec index access — can the index be out of bounds on a real input (panic)?

## Where the detection code lives
- **Rule:** [`infra/rust/edge-case/rust-hardening.yaml`](../../../infra/rust/edge-case/rust-hardening.yaml) — Semgrep rule `waypoint-rust-panicking-index`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-panicking-index`
- **Also flagged by (when that tool is installed):** clippy `clippy::panic` / `clippy::unwrap_used`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-panicking-index", "level": "note",
  "properties": { "waypoint": {
    "axes": ["edge-case"], "severity_prior": 0.3,
    "hypothesis": "slice/Vec index access — can the index be out of bounds on a real input (panic)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-panicking-index" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-panicking-index
    items[idx]
}
```
