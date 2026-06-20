# `waypoint-rust-logic-bool-literal-compare`

> Beacon schema — generated from `infra/rust/logic/rust-logic.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** logic
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** logic
- **Language(s):** rust

## Agent hypothesis
> bool compared to a literal (== true / == false) — redundant; check the condition isn't inverted.

## Where the detection code lives
- **Rule:** [`infra/rust/logic/rust-logic.yaml`](../../../infra/rust/logic/rust-logic.yaml) — Semgrep rule `waypoint-rust-logic-bool-literal-compare`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-logic-bool-literal-compare`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-logic-bool-literal-compare", "level": "note",
  "properties": { "waypoint": {
    "axes": ["logic"], "severity_prior": 0.3,
    "hypothesis": "bool compared to a literal (== true / == false) — redundant; check the condition isn't inverted.",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-logic-bool-literal-compare" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/logic_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-logic-bool-literal-compare
    if flag == true {
        return true;
```
