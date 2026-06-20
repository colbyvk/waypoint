# `waypoint-ts-unbounded-loop`

> Beacon schema — generated from `infra/typescript/abuse/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** typescript

## Agent hypothesis
> while(true)/for(;;) — can input prevent the break and hang the loop (DoS)?

## Where the detection code lives
- **Rule:** [`infra/typescript/abuse/typescript-hardening.yaml`](../../../infra/typescript/abuse/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-unbounded-loop`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-unbounded-loop`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-unbounded-loop", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "while(true)/for(;;) — can input prevent the break and hang the loop (DoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-unbounded-loop" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-unbounded-loop
  while (true) {
    const item = queue.shift();
```
