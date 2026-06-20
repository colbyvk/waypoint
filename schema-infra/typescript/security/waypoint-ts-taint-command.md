# `waypoint-ts-taint-command`

> Beacon schema — generated from `infra/typescript/security/typescript-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> tainted input reaches a child_process sink — command injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-taint.yaml`](../../../infra/typescript/security/typescript-taint.yaml) — Semgrep rule `waypoint-ts-taint-command`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-taint-command`
- **Also flagged by (when that tool is installed):** eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-taint-command", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "tainted input reaches a child_process sink — command injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-taint-command" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/taint_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-taint-command
  cp.exec("ls " + req.query.dir);
  // WAYPOINT-OK: constant command
```
