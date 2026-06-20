# `waypoint-rust-read-unbounded`

> Beacon schema — generated from `infra/rust/abuse/rust-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** abuse
- **Language(s):** rust

## Agent hypothesis
> read_to_end/read_to_string on input — is the source unbounded/attacker-controlled (memory DoS)?

## Where the detection code lives
- **Rule:** [`infra/rust/abuse/rust-hardening.yaml`](../../../infra/rust/abuse/rust-hardening.yaml) — Semgrep rule `waypoint-rust-read-unbounded`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-read-unbounded`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-read-unbounded", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.6,
    "hypothesis": "read_to_end/read_to_string on input — is the source unbounded/attacker-controlled (memory DoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-read-unbounded" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```rust
// samples/monorepo/rust_service/src/hardening_samples.rs
    // WAYPOINT-PLANT: waypoint-rust-read-unbounded
    r.read_to_end(&mut buf)?;
    Ok(buf)
```
