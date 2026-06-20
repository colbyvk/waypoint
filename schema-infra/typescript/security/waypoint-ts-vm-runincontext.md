# `waypoint-ts-vm-runincontext`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> vm.runIn*Context on a non-literal — code injection / RCE (vm is not a sandbox)?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening2.yaml`](../../../infra/typescript/security/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-vm-runincontext`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-vm-runincontext`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-vm-runincontext", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "vm.runIn*Context on a non-literal — code injection / RCE (vm is not a sandbox)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-vm-runincontext" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-vm-runincontext
  return vm.runInNewContext(src, {});
}
```
