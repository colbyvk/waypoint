# `waypoint-react-dangerous-html`

> Beacon schema — generated from `infra/react/security/react.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> dangerouslySetInnerHTML from non-constant — XSS?

## Where the detection code lives
- **Rule:** [`infra/react/security/react.yaml`](../../../infra/react/security/react.yaml) — Semgrep rule `waypoint-react-dangerous-html`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-dangerous-html`
- **Also flagged by (when that tool is installed):** eslint `security/*`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-dangerous-html", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "dangerouslySetInnerHTML from non-constant — XSS?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-dangerous-html" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).
