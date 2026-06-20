# `gitleaks` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **gitleaks** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `gitleaks` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF (`--report-format sarif`).
- **Tagged by:** `tag_map.yaml` → `tools.gitleaks`.

- **Default axes:** security
- **Default hypothesis:** Possible secret ({rule}) at {file}:{line} — is it live, and is it in git history?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
