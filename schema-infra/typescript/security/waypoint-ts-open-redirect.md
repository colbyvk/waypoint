# `waypoint-ts-open-redirect`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> non-literal redirect/location target — open redirect from user input?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening.yaml`](../../../infra/typescript/security/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-open-redirect`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-open-redirect`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-open-redirect", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "non-literal redirect/location target — open redirect from user input?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-open-redirect" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-open-redirect
  window.location.href = target;
}
```
