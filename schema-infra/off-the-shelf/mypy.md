# `mypy` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **mypy** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `mypy` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** text → `detectors/normalize/mypy_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.mypy`.

- **Default axes:** edge-case
- **Default hypothesis:** mypy: {message} in {symbol} — can this type hole produce a runtime None-deref / attribute error on a real path?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `union-attr` | edge-case | attribute access on an Optional in {symbol} — can it be None at runtime (None-deref)? |
| `arg-type` | edge-case | argument type mismatch in {symbol} — real call site that passes the wrong type? |
| `return-value` | edge-case | return type mismatch in {symbol} — does a caller mishandle the value? |
| `unreachable` | logic | mypy proved this code unreachable in {symbol} — dead branch, impossible condition, or an early return/raise bug? |
| `comparison-overlap` | logic | == / != between non-overlapping types in {symbol} — this comparison is always False; a type-confusion bug? |
| `return` | logic | a path through {symbol} falls through with no return — does it silently yield None where a value is expected? |
