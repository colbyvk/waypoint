# `waypoint-ts-child-process-shell`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> spawn/execFile with shell:true — command injection via shell metacharacters?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening.yaml`](../../../infra/typescript/security/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-child-process-shell`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-child-process-shell`
- **Also flagged by (when that tool is installed):** bandit `B605` (start_process_with_a_shell); eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-child-process-shell", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "spawn/execFile with shell:true — command injection via shell metacharacters?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-child-process-shell" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-child-process-shell
  return spawn(cmd, [], { shell: true });
}
```
