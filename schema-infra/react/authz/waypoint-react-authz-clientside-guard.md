# `waypoint-react-authz-clientside-guard`

> Beacon schema — generated from `infra/react/authz/react-authz.yaml` by `detectors/gen_schema_infra.py`. Do not edit by hand.

- **Axes:** security, abuse
- **Severity:** `INFO` → SARIF `note` → `severity_prior` ≈ 0.3
- **Category:** security
- **Language(s):** typescript

## Agent hypothesis
> authorization decided client-side (isAdmin/role===admin) — is the same check enforced server-side, or is it bypassable?

## Where the detection code lives
- **Rule:** [`infra/react/authz/react-authz.yaml`](../../../infra/react/authz/react-authz.yaml) — Semgrep rule `waypoint-react-authz-clientside-guard`
- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.

## Which linters raise this beacon
- **Primary:** Semgrep — rule `waypoint-react-authz-clientside-guard`

## Beacon this rule emits
```jsonc
{ "ruleId": "waypoint-react-authz-clientside-guard", "level": "note",
  "properties": { "waypoint": {
    "axes": ["security", "abuse"], "severity_prior": 0.3,
    "hypothesis": "authorization decided client-side (isAdmin/role===admin) — is the same check enforced server-side, or is it bypassable?",
    "content_hash": "…", "tool": "semgrep", "rule_id": "waypoint-react-authz-clientside-guard" }} }}
```
`score` / `rank` / `boundary_reachable` / `centrality` are added by `prioritise/rank.py`; `merged_from` lists every detector if this region is deduped with another tool. See [the shared schema](../../README.md).

## Example region it fires on
```tsx
// samples/monorepo/react_app/src/AuthzSamples.tsx
      {/* WAYPOINT-PLANT: waypoint-react-authz-clientside-guard */}
      {user.isAdmin && <button>Delete everything</button>}
      {/* WAYPOINT-OK: login state, not a privilege gate */}
```
