# `waypoint-ts-timer-leak`

> Beacon schema — generated from `infra/typescript/concurrency/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> setInterval / self-rescheduling setTimeout — handle never cleared or ticks overlap?

## Where the detection code lives
- **Rule:** [`infra/typescript/concurrency/typescript-hardening.yaml`](../../../infra/typescript/concurrency/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-timer-leak`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-timer-leak`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-timer-leak", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "setInterval / self-rescheduling setTimeout — handle never cleared or ticks overlap?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-timer-leak" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-timer-leak
  setInterval(() => poll(), 1000);
}
```
