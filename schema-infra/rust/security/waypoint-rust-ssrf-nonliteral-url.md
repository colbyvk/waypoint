# `waypoint-rust-ssrf-nonliteral-url`

> Beacon schema — generated from `infra/rust/security/rust-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** rust

## Agent hypothesis
> reqwest::get / Client send with a non-literal URL — SSRF if destination is user-controlled?

## Where the detection code lives
- **Rule:** [`infra/rust/security/rust-hardening2.yaml`](../../../infra/rust/security/rust-hardening2.yaml) — Semgrep rule `waypoint-rust-ssrf-nonliteral-url`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-ssrf-nonliteral-url`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-ssrf-nonliteral-url", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "reqwest::get / Client send with a non-literal URL — SSRF if destination is user-controlled?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-ssrf-nonliteral-url" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening2.rs
    // WAYPOINT-PLANT: waypoint-rust-ssrf-nonliteral-url
    reqwest::get(url).await.unwrap().text().await.unwrap()
}
```
