# `waypoint-rust-concurrency-primitive`

> Beacon schema — generated from `infra/rust/concurrency/rust.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** rust

## Agent hypothesis
> spawn/Arc present — unsynchronized shared-state access nearby?

## Where the detection code lives
- **Rule:** [`infra/rust/concurrency/rust.yaml`](../../../infra/rust/concurrency/rust.yaml) — Semgrep rule `waypoint-rust-concurrency-primitive`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-rust-concurrency-primitive`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-rust-concurrency-primitive", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "spawn/Arc present — unsynchronized shared-state access nearby?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-rust-concurrency-primitive" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/rust-concurrency-primitive.md`](../../../hazards/rust-concurrency-primitive.md)
