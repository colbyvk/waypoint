# `waypoint-rust-tempfile-predictable`

> Beacon schema — generated from `infra/rust/security/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, edge-case
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> predictable temp path (temp_dir().join(const) / fixed /tmp path) — symlink/TOCTOU race?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening2.yaml`](../../../infra/rust/security/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-tempfile-predictable`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-tempfile-predictable`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-tempfile-predictable", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security", "edge-case"], "severity_prior": 0.6,
    "hypothesis": "predictable temp path (temp_dir().join(const) / fixed /tmp path) — symlink/TOCTOU race?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-tempfile-predictable" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-tempfile-predictable
    env::temp_dir().join("waypoint-cache.tmp")
}
```
