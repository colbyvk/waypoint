# `cargo-mutants` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **cargo-mutants** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `cargo-mutants` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** outcomes.json → `detectors/normalize/mutants_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.cargo-mutants`.

- **Default axes:** logic
- **Default hypothesis:** surviving mutant in {symbol} — is this branch untested, or is the logic wrong?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
