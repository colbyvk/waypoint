# `waypoint-ts-weak-jwt`

> Beacon schema — generated from `infra/typescript/security/typescript-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> JWT alg none or decode-as-verify — signature not enforced (auth bypass)?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript-hardening.yaml`](../../../infra/typescript/security/typescript-hardening.yaml) — Semgrep rule `waypoint-ts-weak-jwt`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-weak-jwt`
- **Also flagged by (when that tool is installed):** bandit `B501`; ruff `S501`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-weak-jwt", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "JWT alg none or decode-as-verify — signature not enforced (auth bypass)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-weak-jwt" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```typescript
// samples/monorepo/ts_lib/src/hardening_samples.ts
  // WAYPOINT-PLANT: waypoint-ts-weak-jwt
  return jwt.verify(token, "secret", { algorithms: ["none"] });
}
```
