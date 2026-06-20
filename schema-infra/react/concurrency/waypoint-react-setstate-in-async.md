# `waypoint-react-setstate-in-async`

> Beacon schema — generated from `infra/react/concurrency/react.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> setState inside async callback — stale-closure / out-of-order update race?

## Where the detection code lives
- **Rule:** [`infra/react/concurrency/react.yaml`](../../../infra/react/concurrency/react.yaml) — Semgrep rule `waypoint-react-setstate-in-async`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-setstate-in-async`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-setstate-in-async", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency", "edge-case"], "severity_prior": 0.3,
    "hypothesis": "setState inside async callback — stale-closure / out-of-order update race?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-setstate-in-async" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/react-setstate-in-async.md`](../../../hazards/react-setstate-in-async.md)
