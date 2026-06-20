# `waypoint-py-insecure-tempfile-mktemp`

> Beacon schema — generated from `infra/python/security/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, edge-case
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> tempfile.mktemp() — predictable temp path with a create-time race (symlink/TOCTOU)?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening2.yaml`](../../../infra/python/security/python-hardening2.yaml) — Semgrep rule `waypoint-py-insecure-tempfile-mktemp`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-insecure-tempfile-mktemp`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-insecure-tempfile-mktemp", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security", "edge-case"], "severity_prior": 0.9,
    "hypothesis": "tempfile.mktemp() — predictable temp path with a create-time race (symlink/TOCTOU)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-insecure-tempfile-mktemp" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-insecure-tempfile-mktemp
    path = tempfile.mktemp()
    with open(path, "w") as f:
```
