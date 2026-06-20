# `waypoint-ts-unbounded-allocation`

> Beacon schema — generated from `infra/typescript/abuse/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** abuse
- **Language(s):** typescript

## Agent hypothesis
> new Array(n) with non-literal n — attacker-controlled size forces giant allocation?

## Where the detection code lives
- **Rule:** [`infra/typescript/abuse/typescript-hardening.yaml`](../../../infra/typescript/abuse/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-unbounded-allocation`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-unbounded-allocation`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-unbounded-allocation", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.6,
    "hypothesis": "new Array(n) with non-literal n — attacker-controlled size forces giant allocation?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-unbounded-allocation" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-unbounded-allocation
  return new Array(n);
}
```
