# `waypoint-rust-unbounded-channel-near-spawn`

> Beacon schema — generated from `infra/rust/concurrency/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> unbounded mpsc::channel near spawn — no backpressure, queue grows unbounded?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust-hardening2.yaml`](../../../infra/rust/concurrency/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-unbounded-channel-near-spawn`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-unbounded-channel-near-spawn`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-unbounded-channel-near-spawn", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency", "abuse"], "severity_prior": 0.3,
    "hypothesis": "unbounded mpsc::channel near spawn — no backpressure, queue grows unbounded?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-unbounded-channel-near-spawn" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-unbounded-channel-near-spawn
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
```
