# `waypoint-py-taint-command`

> Beacon schema — generated from `infra/python/security/python-taint.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> tainted input reaches a command/shell sink — injection along this dataflow?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-taint.yaml`](../../../infra/python/security/python-taint.yaml) — Semgrep rule `waypoint-py-taint-command`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-taint-command`
- **Also flagged by (when that tool is installed):** bandit `B605` (start_process_with_a_shell); eslint `security/detect-child-process`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-taint-command", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "tainted input reaches a command/shell sink — injection along this dataflow?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-taint-command" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/taint_samples.py
    # WAYPOINT-PLANT: waypoint-py-taint-command
    os.system("ping -c1 " + host)
    # WAYPOINT-OK: constant command
```
