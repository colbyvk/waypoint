# `waypoint-react-untrusted-prop-spread`

> Beacon schema — generated from `infra/react/security/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> spread of an arbitrary object into JSX props — prop injection (dangerouslySetInnerHTML / href / handlers)?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening.yaml`](../../../infra/react/security/react-hardening.yaml) — Semgrep rule `waypoint-react-untrusted-prop-spread`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-untrusted-prop-spread`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-untrusted-prop-spread", "level": "note",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.3,
    "hypothesis": "spread of an arbitrary object into JSX props — prop injection (dangerouslySetInnerHTML / href / handlers)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-untrusted-prop-spread" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-untrusted-prop-spread [axes: security,abuse] */}
      <button {...attrs}>click</button>

```
