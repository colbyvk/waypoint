# `waypoint-react-create-markup-helper`

> Beacon schema — generated from `infra/react/security/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security
- **Severity:** `WARNING` → SARIF `warning` → `severity_prior` ≈ 0.6
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> createMarkup-style {__html} factory from a dynamic value — unsanitized HTML into dangerouslySetInnerHTML (XSS)?

## Where the detection code lives
- **Rule:** [`infra/react/security/react-hardening.yaml`](../../../infra/react/security/react-hardening.yaml) — Semgrep rule `waypoint-react-create-markup-helper`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-create-markup-helper`
- **Also flagged by (when that tool is installed):** eslint `security/*`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-create-markup-helper", "level": "warning",
  "properties": { "waypoint": {
    "axes": ["security"], "severity_prior": 0.6,
    "hypothesis": "createMarkup-style {__html} factory from a dynamic value — unsanitized HTML into dangerouslySetInnerHTML (XSS)?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-create-markup-helper" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-create-markup-helper [axes: security] */}
      <div dangerouslySetInnerHTML={createMarkup(htmlBlob)} />
    </div>
```
