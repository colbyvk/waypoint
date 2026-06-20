# `waypoint-react-heavy-work-in-render`

> Beacon schema — generated from `infra/react/abuse/react-hardening.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** abuse
- **Language(s):** typescript

## Agent hypothesis
> new RegExp / JSON.parse / .sort() in render path — per-render CPU amplification on large input?

## Where the detection code lives
- **Rule:** [`infra/react/abuse/react-hardening.yaml`](../../../infra/react/abuse/react-hardening.yaml) — Semgrep rule `waypoint-react-heavy-work-in-render`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-heavy-work-in-render`
- **Also flagged by (when that tool is installed):** bandit `B108`; eslint `security/detect-non-literal-fs-filename`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-heavy-work-in-render", "level": "note",
  "properties": { "waypoint": {
    "axes": ["abuse"], "severity_prior": 0.3,
    "hypothesis": "new RegExp / JSON.parse / .sort() in render path — per-render CPU amplification on large input?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-heavy-work-in-render" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/HardeningSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-heavy-work-in-render [axes: abuse] */}
      <p>{items.filter((x) => new RegExp("^a").test(x)).length}</p>
    </div>
```
