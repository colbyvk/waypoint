# `npm-audit` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **npm-audit** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `npm-audit` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** JSON → normalizer.
- **Tagged by:** `tag_map.yaml` → `tools.npm-audit`.

- **Default axes:** security
- **Default hypothesis:** npm advisory {rule} in a dependency — reachable from app code?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
