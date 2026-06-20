# `race-detector` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **race-detector** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `race-detector` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** Go `-race` / TSan text → `detectors/normalize/race_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.race-detector`.

- **Default axes:** logic, concurrency
- **Default hypothesis:** runtime data race at {file}:{line} — confirm the unsynchronized shared access and interleaving.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
