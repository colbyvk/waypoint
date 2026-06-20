# `waypoint-ts-taint-sql`

> Beacon schema — generated from `infra/typescript/security/typescript-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> tainted input reaches a SQL query string — injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-taint.yaml`](../../../infra/typescript/security/typescript-taint.yaml) — Semgrep rule `waypoint-ts-taint-sql`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-taint-sql`
- **Also flagged by (when that tool is installed):** bandit `B608` (SQL injection); ruff `S608` (hardcoded-sql)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-taint-sql", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.9,
    "hypothesis": "tainted input reaches a SQL query string — injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-taint-sql" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/taint_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-taint-sql
  db.query("SELECT * FROM u WHERE n = '" + req.body.name + "'");
  // WAYPOINT-OK: parametrized — query string is constant
```
