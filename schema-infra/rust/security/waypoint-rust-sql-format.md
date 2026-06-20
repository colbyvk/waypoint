# `waypoint-rust-sql-format`

> Beacon schema — generated from `infra/rust/security/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> query/execute(format!(...)) — does an interpolated value reach the SQL string (injection)?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening.yaml`](../../../infra/rust/security/rust-hardening.yaml) — Semgrep rule `waypoint-rust-sql-format`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-sql-format`
- **Also flagged by (when that tool is installed):** bandit `B608` (SQL injection); ruff `S608` (hardcoded-sql)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-sql-format", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "query/execute(format!(...)) — does an interpolated value reach the SQL string (injection)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-sql-format" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-sql-format
    let q = sqlx::query(&format!("SELECT * FROM users WHERE name = '{}'", name));
    // WAYPOINT-PLANT: waypoint-rust-sql-format
```
