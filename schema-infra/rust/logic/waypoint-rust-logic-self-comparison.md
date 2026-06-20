# `waypoint-rust-logic-self-comparison`

> Beacon schema — generated from `infra/rust/logic/rust-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** logic
- **Language(s):** rust

## Agent hypothesis
> self-comparison ($X == $X / != $X) is constant — likely a typo for a different operand?

## Where the detection code lives
- **Rule:** [`infra/rust/logic/rust-logic.yaml`](../../../infra/rust/logic/rust-logic.yaml) — Semgrep rule `waypoint-rust-logic-self-comparison`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-logic-self-comparison`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-logic-self-comparison", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.6,
    "hypothesis": "self-comparison ($X == $X / != $X) is constant — likely a typo for a different operand?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-logic-self-comparison" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/logic_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-logic-self-comparison
    if a == a {
        return true;
```
