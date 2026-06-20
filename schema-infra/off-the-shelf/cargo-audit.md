# `cargo-audit` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **cargo-audit** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `cargo-audit` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** JSON (advisory) → normalizer.
- **Tagged by:** `tag_map.yaml` → `tools.cargo-audit`.

- **Default axes:** security
- **Default hypothesis:** RustSec advisory {rule} affects a dependency used near {symbol} — is the vulnerable path actually reachable?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| _(default only)_ | — | — |
