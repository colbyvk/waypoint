# `waypoint-rust-unbounded-recursion`

> Beacon schema — generated from `infra/rust/abuse/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** rust

## Agent hypothesis
> self-recursive fn with no visible depth bound — input-driven stack overflow (DoS)?

## Where the detection code lives
- **Rule:** [`infra/rust/abuse/rust-hardening2.yaml`](../../../infra/rust/abuse/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-unbounded-recursion`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-unbounded-recursion`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-unbounded-recursion", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "self-recursive fn with no visible depth bound — input-driven stack overflow (DoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-unbounded-recursion" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-unbounded-recursion
    acc.push(node.value);
    for child in &node.children {
```
