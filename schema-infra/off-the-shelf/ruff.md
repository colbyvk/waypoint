# `ruff` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **ruff** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `ruff` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF (`ruff check --output-format sarif`).
- **Tagged by:** `tag_map.yaml` → `tools.ruff`.

- **Default axes:** edge-case
- **Default hypothesis:** Ruff {rule} in {symbol} — confirm whether this is a real correctness issue.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `S307` | security | eval-like call in {symbol} — attacker-controlled input? |
| `S608` | security, abuse | string-built SQL in {symbol} — injection via unparametrized user input? |
| `S60*` | security | subprocess/shell in {symbol} — command injection via user input? |
| `S501` | security | TLS verification disabled in {symbol} — MITM exposure? |
| `S105` | security | possible hardcoded secret in {symbol} — live credential? |
| `S106` | security | possible hardcoded secret passed as argument in {symbol} — live credential? |
| `S110` | edge-case | try/except/pass in {symbol} — which error is silently dropped? |
| `S112` | edge-case | try/except/continue in {symbol} — which error is silently dropped? |
| `S311` | security | non-cryptographic RNG used in {symbol} — is it used for a security decision? |
| `E722` | edge-case | bare except in {symbol} — what is being swallowed, including KeyboardInterrupt? |
| `ASYNC*` | concurrency | async hazard {rule} in {symbol} — blocking call or task race inside async code? |
| `B008` | edge-case | function call in default argument of {symbol} — shared-mutable-default bug? |
| `B904` | edge-case | raise without from inside except in {symbol} — losing the original cause? |
