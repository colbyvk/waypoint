# `hypothesis` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **hypothesis** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `hypothesis` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** pytest+Hypothesis output → `detectors/normalize/hypothesis_to_sarif.py` (carries the shrunk reproducing input).
- **Tagged by:** `tag_map.yaml` → `tools.hypothesis`.

- **Default axes:** logic, edge-case
- **Default hypothesis:** Hypothesis falsified a property in {symbol} — confirm the code is wrong (not the property); see the shrunk reproducing input.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
