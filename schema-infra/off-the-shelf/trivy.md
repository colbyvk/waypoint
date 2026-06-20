# `trivy` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **trivy** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `trivy` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF (`trivy fs --format sarif`).
- **Tagged by:** `tag_map.yaml` → `tools.trivy`.

- **Default axes:** security
- **Default hypothesis:** Trivy reports {rule} in a dependency — confirm reachability and whether a fixed version exists.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
