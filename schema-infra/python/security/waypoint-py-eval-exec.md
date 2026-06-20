# `waypoint-py-eval-exec`

> Beacon schema — generated from `infra/python/security/python.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> eval/exec on a non-literal — attacker-controlled input reachable?

## Where the detection code lives
- **Rule:** [`infra/python/security/python.yaml`](../../../infra/python/security/python.yaml) — Semgrep rule `waypoint-py-eval-exec`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-eval-exec`
- **Also flagged by (when that tool is installed):** bandit `B307` (eval); ruff `S307` (suspicious-eval); eslint `security/detect-eval-with-expression`; bandit `B102` (exec_used)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-eval-exec", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "eval/exec on a non-literal — attacker-controlled input reachable?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-eval-exec" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## See also
- Plain-English hazard: [`hazards/eval-exec.md`](../../../hazards/eval-exec.md)
