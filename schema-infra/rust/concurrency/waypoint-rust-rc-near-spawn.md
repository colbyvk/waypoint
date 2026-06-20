# `waypoint-rust-rc-near-spawn`

> Beacon schema — generated from `infra/rust/concurrency/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> Rc::new near thread::spawn — is a non-Send Rc moved across a thread boundary?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust-hardening.yaml`](../../../infra/rust/concurrency/rust-hardening.yaml) — Semgrep rule `waypoint-rust-rc-near-spawn`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-rc-near-spawn`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-rc-near-spawn", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "Rc::new near thread::spawn — is a non-Send Rc moved across a thread boundary?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-rc-near-spawn" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-rc-near-spawn
    let shared = Rc::new(42u64);
    let h = thread::spawn(move || {
```
