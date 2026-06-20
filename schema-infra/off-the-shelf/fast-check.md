# `fast-check` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **fast-check** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `fast-check` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** jest/vitest+fast-check output → `detectors/normalize/fastcheck_to_sarif.py` (carries the counterexample).
- **Tagged by:** `tag_map.yaml` → `tools.fast-check`.

- **Default axes:** logic, edge-case
- **Default hypothesis:** fast-check falsified a property in {symbol} — confirm the code is wrong (not the property); see the counterexample.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
