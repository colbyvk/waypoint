# `fuzz` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **fuzz** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `fuzz` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** cargo-fuzz / atheris / jazzer.js crash text → `detectors/normalize/fuzz_to_sarif.py` (carries the crashing input).
- **Tagged by:** `tag_map.yaml` → `tools.fuzz`.

- **Default axes:** logic, edge-case
- **Default hypothesis:** fuzz-found crash in {symbol} — bound/validate the offending input or handle the case.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
