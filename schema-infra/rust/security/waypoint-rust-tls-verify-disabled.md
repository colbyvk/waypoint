# `waypoint-rust-tls-verify-disabled`

> Beacon schema — generated from `infra/rust/security/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> danger_accept_invalid_certs(true) / SslVerifyMode::NONE — TLS verification off (MITM)?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening2.yaml`](../../../infra/rust/security/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-tls-verify-disabled`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-tls-verify-disabled`
- **Also flagged by (when that tool is installed):** bandit `B501` (request_with_no_cert_validation); ruff `S501`; bandit `B501`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-tls-verify-disabled", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "danger_accept_invalid_certs(true) / SslVerifyMode::NONE — TLS verification off (MITM)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-tls-verify-disabled" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-tls-verify-disabled
    reqwest::Client::builder().danger_accept_invalid_certs(true).build().unwrap()
}
```
