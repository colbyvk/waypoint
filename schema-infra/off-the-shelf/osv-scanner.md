# `osv-scanner` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **osv-scanner** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `osv-scanner` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF.
- **Tagged by:** `tag_map.yaml` → `tools.osv-scanner`.

- **Default axes:** security
- **Default hypothesis:** OSV advisory {rule} in a dependency — is the vulnerable function actually invoked?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
