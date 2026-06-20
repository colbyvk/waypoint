# `eslint` beacons (off-the-shelf detector)

> Generated from `tag_map.yaml`. Waypoint runs **eslint** as-is (spec §13: install, don't reimplement) and tags its findings.

## Where the detection code lives
- **Engine:** the `eslint` tool and its built-in rule packs (not Waypoint code).
- **Into SARIF via:** native SARIF (`@microsoft/eslint-formatter-sarif`).
- **Tagged by:** `tag_map.yaml` → `tools.eslint`.

- **Default axes:** edge-case
- **Default hypothesis:** ESLint {rule} in {symbol} — real correctness issue?

## Rule-id → axes mapping (`tag_map.yaml`)
| rule-id match | axes | agent hypothesis |
|---|---|---|
| `security/detect-eval-with-expression` | security | eval with a dynamic expression in {symbol} — attacker-controlled input? |
| `security/detect-child-process` | security | child_process invocation in {symbol} — command injection via user input? |
| `security/detect-non-literal-fs-filename` | security | fs path built from a variable in {symbol} — path traversal? |
| `security/detect-unsafe-regex` | abuse, security | regex with catastrophic-backtracking shape in {symbol} — ReDoS on user input? |
| `security/*` | security | ESLint security rule {rule} in {symbol} — confirm exploitability. |
| `react-hooks/exhaustive-deps` | concurrency, edge-case | incomplete useEffect dependency array in {symbol} — stale-closure / missed-update race? |
| `react-hooks/rules-of-hooks` | edge-case | conditional hook call in {symbol} — render-order violation? |
| `*no-non-null-assertion*` | edge-case | non-null assertion (!) in {symbol} — can the value actually be null/undefined here? |
| `*no-floating-promises*` | concurrency, edge-case | unawaited promise in {symbol} — unhandled rejection / ordering race? |
