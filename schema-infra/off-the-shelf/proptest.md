# `proptest` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **proptest** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `proptest` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** cargo test (proptest/quickcheck) output → `detectors/normalize/proptest_to_sarif.py` (carries the minimal failing input).
- **Tagged by:** `tag_map.yaml` → `tools.proptest`.

- **Default axes:** logic, edge-case
- **Default hypothesis:** proptest/quickcheck falsified a property in {symbol} — confirm the code is wrong (not the property); see the minimal failing input.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
