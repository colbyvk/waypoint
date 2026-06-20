# `waypoint-rust-unsafe-send-sync`

> Beacon schema — generated from `infra/rust/concurrency/rust.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> hand-written unsafe Send/Sync — is the cross-thread invariant actually sound?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust.yaml`](../../../infra/rust/concurrency/rust.yaml) — Semgrep rule `waypoint-rust-unsafe-send-sync`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-unsafe-send-sync`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-unsafe-send-sync", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "security"], "severity_prior": 0.6,
    "hypothesis": "hand-written unsafe Send/Sync — is the cross-thread invariant actually sound?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-unsafe-send-sync" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/rust-unsafe-send-sync.md`](../../../hazards/rust-unsafe-send-sync.md)
