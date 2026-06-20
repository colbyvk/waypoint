# `waypoint-ts-child-process`

> Beacon schema — generated from `infra/typescript/security/typescript.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> child_process exec with interpolation — command injection?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript.yaml`](../../../infra/typescript/security/typescript.yaml) — Semgrep rule `waypoint-ts-child-process`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-child-process`
- **Also flagged by (when that tool is installed):** bandit `B102` (exec_used); eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-child-process", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "child_process exec with interpolation — command injection?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-child-process" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-child-process-shell
  return spawn(cmd, [], { shell: true });
}
```
