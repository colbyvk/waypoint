# `clippy` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **clippy** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `clippy` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** cargo JSON → `detectors/normalize/clippy_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.clippy`.

- **Default axes:** edge-case
- **Default hypothesis:** Clippy {rule} in {symbol} — real correctness issue or idiomatic noise?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `*unwrap*` | edge-case | .unwrap() in {symbol} — can the Result/Option actually be Err/None here (panic)? |
| `*expect*` | edge-case | .expect() in {symbol} — reachable panic on a real input? |
| `*panic*` | edge-case | panic! in {symbol} — reachable from untrusted input (DoS)? |
| `*await_holding_lock*` | concurrency | lock held across .await in {symbol} — deadlock / contention across tasks? |
| `*await_holding_refcell*` | concurrency | RefCell ref held across .await in {symbol} — borrow panic across tasks? |
| `*mutex_atomic*` | concurrency | Mutex guarding a primitive in {symbol} — atomics intended; check the locking discipline. |
| `*integer_arithmetic*` | abuse | unchecked integer arithmetic in {symbol} — overflow on attacker-sized input? |
| `*eq_op*` | logic | identical operands on both sides of an operator in {symbol} (clippy eq_op) — a typo for a different operand? |
| `*ifs_same_cond*` | logic | consecutive if/else-if with the same condition in {symbol} — the second branch is dead; wrong condition? |
| `*almost_swapped*` | logic | looks like a botched swap in {symbol} (clippy almost_swapped) — assignment order wrong? |
| `*absurd_extreme_comparisons*` | logic | comparison that is always true/false in {symbol} — bound/condition bug? |
