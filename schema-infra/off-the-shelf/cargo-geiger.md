# `cargo-geiger` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **cargo-geiger** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `cargo-geiger` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** JSON → `detectors/normalize/geiger_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.cargo-geiger`.

- **Default axes:** concurrency, security
- **Default hypothesis:** unsafe code present in {symbol} (cargo-geiger) — does the safety/Send-Sync invariant hold across threads?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
