# `waypoint-rust-static-mut`

> Beacon schema — generated from `infra/rust/concurrency/rust.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> static mut accessed — any concurrent reader/writer (data race)?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust.yaml`](../../../infra/rust/concurrency/rust.yaml) — Semgrep rule `waypoint-rust-static-mut`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-static-mut`
- **Also flagged by (when that tool is installed):** clippy `clippy::static_mut_refs`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-static-mut", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["concurrency", "security"], "severity_prior": 0.6,
    "hypothesis": "static mut accessed — any concurrent reader/writer (data race)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-static-mut" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/rust-static-mut.md`](../../../hazards/rust-static-mut.md)
