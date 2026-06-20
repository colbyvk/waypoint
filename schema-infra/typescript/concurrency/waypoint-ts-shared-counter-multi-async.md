# `waypoint-ts-shared-counter-multi-async`

> Beacon schema — generated from `infra/typescript/concurrency/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> module-level counter ++/-- inside async fn — lost-update race across concurrent invocations?

## Where the detection code lives
- **Rule:** [`infra/typescript/concurrency/typescript-hardening2.yaml`](../../../infra/typescript/concurrency/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-shared-counter-multi-async`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-shared-counter-multi-async`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-shared-counter-multi-async", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency"], "severity_prior": 0.3,
    "hypothesis": "module-level counter ++/-- inside async fn — lost-update race across concurrent invocations?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-shared-counter-multi-async" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-shared-counter-multi-async
  requestCount++;
  await Promise.resolve();
```
