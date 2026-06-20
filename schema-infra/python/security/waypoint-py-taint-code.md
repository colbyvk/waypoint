# `waypoint-py-taint-code`

> Beacon schema — generated from `infra/python/security/python-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> tainted input reaches eval/exec — code injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-taint.yaml`](../../../infra/python/security/python-taint.yaml) — Semgrep rule `waypoint-py-taint-code`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-taint-code`
- **Also flagged by (when that tool is installed):** bandit `B307` (eval); ruff `S307` (suspicious-eval); eslint `security/detect-eval-with-expression`; bandit `B102` (exec_used)

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-taint-code", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "tainted input reaches eval/exec — code injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-taint-code" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/taint_samples.py
    # WAYPOINT-PLANT: waypoint-py-taint-code
    eval(expr)
    # WAYPOINT-OK: constant expression
```
