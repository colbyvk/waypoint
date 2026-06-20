# `waypoint-py-minidom-entity-expansion`

> Beacon schema — generated from `infra/python/abuse/python-hardening2.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse, security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** abuse
- **Language(s):** python

## Agent hypothesis
> minidom/expat parse of untrusted XML with no entity cap — billion-laughs expansion DoS?

## Where the detection code lives
- **Rule:** [`infra/python/abuse/python-hardening2.yaml`](../../../infra/python/abuse/python-hardening2.yaml) — Semgrep rule `waypoint-py-minidom-entity-expansion`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-py-minidom-entity-expansion`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-py-minidom-entity-expansion", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["abuse", "security"], "severity_prior": 0.6,
    "hypothesis": "minidom/expat parse of untrusted XML with no entity cap — billion-laughs expansion DoS?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-py-minidom-entity-expansion" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```python
# samples/monorepo/py_service/hardening2.py
    # WAYPOINT-PLANT: waypoint-py-minidom-entity-expansion
    return xml.dom.minidom.parseString(xml_text)

```
