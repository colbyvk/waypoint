# `bandit` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **bandit** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `bandit` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** JSON → `detectors/normalize/bandit_to_sarif.py`.
- **Tagged by:** `tag_map.yaml` → `tools.bandit`.

- **Default axes:** security
- **Default hypothesis:** Bandit {rule} flagged a security shape in {symbol}. Confirm exploitability given how this code is reached.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `B102` | security | exec() on a non-constant value in {symbol} — can attacker-controlled input reach it? |
| `B307` | security | eval() on a non-constant value in {symbol} — can attacker-controlled input reach it? |
| `B608` | security, abuse | SQL built by string ops in {symbol} — does user input reach this query unparametrized (injection)? |
| `B60*` | security | subprocess/shell invocation in {symbol} — is any argument attacker-controlled (command injection)? |
| `B501` | security | TLS certificate validation disabled near {symbol} — MITM exposure on this request? |
| `B10[567]` | security | Possible hardcoded credential in {symbol} — is this a live secret? |
| `B11[02]` | edge-case | try/except swallows the error in {symbol} — what failure is being hidden? |
| `B30[12]` | security | Unpickling untrusted data in {symbol} — deserialization RCE? |
