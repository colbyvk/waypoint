# `waypoint-rust-infinite-loop`

> Beacon schema — generated from `infra/rust/abuse/rust-loops.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** rust

## Agent hypothesis
> infinite loop (loop / while true) — bounded exit, or a dead loop / CPU busy-spin?

## Where the detection code lives
- **Rule:** [`infra/rust/abuse/rust-loops.yaml`](../../../infra/rust/abuse/rust-loops.yaml) — Semgrep rule `waypoint-rust-infinite-loop`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-infinite-loop`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-infinite-loop", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "infinite loop (loop / while true) — bounded exit, or a dead loop / CPU busy-spin?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-infinite-loop" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/loops.rs
    // WAYPOINT-PLANT: waypoint-rust-infinite-loop
    loop {
        handle();
```
