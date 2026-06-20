# `pip-audit` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **pip-audit** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `pip-audit` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** JSON → `detectors/normalize/pipaudit_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.pip-audit`.

- **Default axes:** security
- **Default hypothesis:** Known CVE {rule} in a Python dependency — is the vulnerable API called from this codebase?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
