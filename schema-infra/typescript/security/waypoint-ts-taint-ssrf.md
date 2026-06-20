# `waypoint-ts-taint-ssrf`

> Beacon schema — generated from `infra/typescript/security/typescript-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> tainted input reaches an HTTP-client URL — SSRF along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-taint.yaml`](../../../infra/typescript/security/typescript-taint.yaml) — Semgrep rule `waypoint-ts-taint-ssrf`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-taint-ssrf`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-taint-ssrf", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "tainted input reaches an HTTP-client URL — SSRF along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-taint-ssrf" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/taint_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-taint-ssrf
  axios.get(req.query.url);
  // WAYPOINT-OK: constant url
```
