# `waypoint-py-ldap-filter-fstring`

> Beacon schema — generated from `infra/python/security/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `ERROR` → SARIF `error` → `severity_prior` ≈ 0.9
- **Category:** security
- **Language(s):** python

## Agent hypothesis
> LDAP search() filter built via f-string/format — LDAP injection from unescaped input?

## Where the detection code lives
- **Rule:** [`infra/python/security/python-hardening2.yaml`](../../../infra/python/security/python-hardening2.yaml) — Semgrep rule `waypoint-py-ldap-filter-fstring`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-ldap-filter-fstring`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-ldap-filter-fstring", "level": "error",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.9,
    "hypothesis": "LDAP search() filter built via f-string/format — LDAP injection from unescaped input?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-ldap-filter-fstring" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-ldap-filter-fstring
    return conn.search("dc=example,dc=com", ldap.SCOPE_SUBTREE, f"(uid={username})")

```
