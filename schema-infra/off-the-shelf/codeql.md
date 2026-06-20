# `codeql` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **codeql** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `codeql` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF.
- **Tagged by:** `tag_map.yaml` → `tools.codeql`.

- **Default axes:** security
- **Default hypothesis:** CodeQL {rule} traced a data flow into {symbol} — confirm the source is untrusted and the sink is dangerous along this path.

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `*sql*` | security, abuse | CodeQL traced tainted data into a SQL sink in {symbol} — confirm injection along the reported path. |
| `*path-injection*` | security | CodeQL traced tainted data into a filesystem path in {symbol} — confirm traversal. |
| `*xss*` | security | CodeQL traced tainted data into an HTML sink in {symbol} — confirm XSS. |
| `*command*` | security | CodeQL traced tainted data into a command sink in {symbol} — confirm injection. |
