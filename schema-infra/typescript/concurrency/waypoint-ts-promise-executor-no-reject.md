# `waypoint-ts-promise-executor-no-reject`

> Beacon schema — generated from `infra/typescript/concurrency/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** concurrency, edge-case
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** concurrency
- **Language(s):** typescript

## Agent hypothesis
> new Promise executor with resolve but no reject — error path leaves promise hung?

## Where the detection code lives
- **Rule:** [`infra/typescript/concurrency/typescript-hardening2.yaml`](../../../infra/typescript/concurrency/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-promise-executor-no-reject`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-promise-executor-no-reject`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-promise-executor-no-reject", "level": "note",
  "properties": { "waypoint": {
    "axes": ["concurrency", "edge-case"], "severity_prior": 0.3,
    "hypothesis": "new Promise executor with resolve but no reject — error path leaves promise hung?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-promise-executor-no-reject" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-promise-executor-no-reject
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
```
