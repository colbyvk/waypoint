# `waypoint-ts-eval`

> Beacon schema — generated from `infra/typescript/security/typescript.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> eval/new Function on dynamic input — code injection?

## Where the detection code lives
- **Rule:** [`infra/typescript/security/typescript.yaml`](../../../infra/typescript/security/typescript.yaml) — Semgrep rule `waypoint-ts-eval`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-ts-eval`
- **Also flagged by (when that tool is installed):** bandit `B307` (eval); ruff `S307` (suspicious-eval); eslint `security/detect-eval-with-expression`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-ts-eval", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "eval/new Function on dynamic input — code injection?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-ts-eval" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
