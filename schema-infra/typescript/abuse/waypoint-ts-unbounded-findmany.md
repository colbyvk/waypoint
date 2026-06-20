# `waypoint-ts-unbounded-findmany`

> Beacon schema — generated from `infra/typescript/abuse/typescript-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** typescript

## Agent hypothesis
> findMany() with no take/limit — unbounded result set (missing pagination, memory DoS)?

## Where the detection code lives
- **Rule:** [`infra/typescript/abuse/typescript-hardening2.yaml`](../../../infra/typescript/abuse/typescript-hardening2.yaml) — Semgrep rule `waypoint-ts-unbounded-findmany`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-unbounded-findmany`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-unbounded-findmany", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "findMany() with no take/limit — unbounded result set (missing pagination, memory DoS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-unbounded-findmany" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening2.ts
  // WAYPOINT-PLANT: waypoint-ts-unbounded-findmany
  return prisma.user.findMany();
}
```
