# `waypoint-rust-alloc-from-size`

> Beacon schema — generated from `infra/rust/abuse/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** abuse
- **Language(s):** rust

## Agent hypothesis
> Vec::with_capacity/reserve with a variable size — is the size attacker-controlled and unbounded?

## Where the detection code lives
- **Rule:** [`infra/rust/abuse/rust-hardening.yaml`](../../../infra/rust/abuse/rust-hardening.yaml) — Semgrep rule `waypoint-rust-alloc-from-size`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-alloc-from-size`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-alloc-from-size", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.6,
    "hypothesis": "Vec::with_capacity/reserve with a variable size — is the size attacker-controlled and unbounded?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-alloc-from-size" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-alloc-from-size
    let mut v: Vec<u8> = Vec::with_capacity(n);
    // WAYPOINT-PLANT: waypoint-rust-alloc-from-size
```
