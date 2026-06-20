# `waypoint-rust-unsafe-block`

> Beacon schema — generated from `infra/rust/security/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> raw unsafe block — is any memory/thread-safety invariant violable on a real input?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening.yaml`](../../../infra/rust/security/rust-hardening.yaml) — Semgrep rule `waypoint-rust-unsafe-block`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-unsafe-block`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-unsafe-block", "level": "note",
  "properties": { "waypoint": {
    "axes": ["security", "concurrency"], "severity_prior": 0.3,
    "hypothesis": "raw unsafe block — is any memory/thread-safety invariant violable on a real input?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-unsafe-block" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-unsafe-block
    let v = unsafe { *p };
    v
```
