# Waypoint

> **Code triage for the AI era** — a $0, deterministic tool your coding agent runs to
> find what's wrong *and* surface what it *couldn't* check. No API key — the agent that
> drives it does the verifying.

[![CI](https://github.com/colbyvk/waypoint/actions/workflows/ci.yml/badge.svg)](https://github.com/colbyvk/waypoint/actions/workflows/ci.yml)
![tests](https://img.shields.io/badge/tests-112%20passing-brightgreen)
![rules](https://img.shields.io/badge/core%20rules-107%20curated-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)
![languages](https://img.shields.io/badge/languages-Python%20%7C%20Rust%20%7C%20TypeScript%20%7C%20React-informational)

**It's a tool, not an agent.** Waypoint runs no model and **needs no API key**. The
agent that *drives* it — Claude Code, Cursor, or you at a terminal — reads the short,
scoped list it produces and verifies each item. Waypoint draws the map; the driver
already has the brain. ([Full README](../README.md))

---

# Validation — does Waypoint actually find real bugs?

An honest, reproducible record of running the **full Waypoint workflow** — scan, then
**open every top beacon's cited `file:line` and confirm it against the actual source**
— on seven public repositories. It answers one question: *when Waypoint flags
something, is it real?*

- **Tier:** `fast` (default) — static only, **$0, no API key**.
- **Workflow:** the intended one — Waypoint drops ranked beacons; a verifier (here,
  agents reading the code, spot-checked by hand) opens each `file:line` and rules it
  **confirmed / contextual / false-positive**. A beacon is a *suspicion*, not a verdict.
- **Date:** 2026-06-20. Raw artifacts (per-beacon `.md`, `INDEX.md`, `ranked.sarif`)
  kept under `hardening/results/validation/<repo>/`.

## Verdict scale

- **Confirmed** — a genuine defect or exploitable/risky pattern on a reachable path; a maintainer would fix or want to know.
- **Contextual** — the flagged pattern is *really there* (the rule fired correctly), but it is safe or intentional in context (e.g. `exec()` on a trusted local config; `assert` in dev-only tooling; a no-auth route that is a public/login endpoint). A true positive for the rule, not an actionable bug.
- **False positive** — the rule misfired; the code is not actually an instance of what it claims.

## Results

| Repo | Kind | Beacons (total) | Scan | Verified | Confirmed | Contextual | False-pos |
|---|---|---:|---:|---:|---:|---:|---:|
| DSVW | deliberately-vulnerable app | 21 | 23s | 21 | **11** | 8 | 2 |
| httpie (`cli`) | HTTP CLI (shipping) | 158 | 6s | 15 | **1** | 9 | 5 |
| Flask | web framework | 108 | 14s | 15 | 0 | 12 | 3 |
| requests | HTTP library | 278 | 13s | 15 | 0 | 14 | 1 |
| werkzeug | WSGI library | 188 | 8s | 15 | 0 | 10 | 5 |
| Django | web framework (~165k LOC) | 4082 | 57s | 15 | 0 | 15 | 0 |
| ky | TypeScript fetch client | 22 | 6s | 22 | 0 | 11 | 11 |
| **Total** | | **4857** | | **118** | **12** | **79** | **27** |

Of the **118 highest-ranked beacons verified by reading the code**, **91 (77%) were
genuine instances** of the flagged pattern (12 actual defects + 79 correctly-identified
but contextually-safe), and **27 (23%) were false positives.** Every scan's coverage
partition held (`analyzed ∪ dark = all functions`).

## The 12 confirmed real issues

**httpie — 1 genuine defect in shipping library code:**
- [`httpie/internal/update_warnings.py:44`] — `requests.get(PACKAGE_INDEX_LINK, verify=False)`: the auto-update version check **disables TLS certificate verification**, exposing it to man-in-the-middle tampering. Low severity (it fetches a version string) but a real defect in code that ships to users.

**DSVW — 11 distinct vulnerabilities confirmed in a deliberately-vulnerable app** (recall proof across real bug classes; every one verified against `dsvw.py`):

| Class | Line | Confirmed code |
|---|---|---|
| Pickle deserialization → RCE | `:35` | `pickle.loads(params["object"].encode())` |
| Remote file inclusion → RCE | `:56`-`57` | fetch attacker URL, then `exec(program, envs)` |
| Command injection | `:39` | `subprocess.run("nslookup " + params["domain"], shell=True)` |
| SQL injection (id) | `:30` | `cursor.execute("SELECT ... WHERE id=" + params["id"])` |
| SQL injection (comment) | `:50` | `INSERT ... VALUES(NULL, '%s', ...) % params["comment"]` |
| SQL injection (login bypass) | `:67` | `password='" + params["password"] + "'` |
| XXE (file read + SSRF) | `:41` | `lxml ... XMLParser(load_dtd=True, resolve_entities=True, no_network=False)` |
| SSRF | `:37` | `urllib.request.urlopen(params["path"])` |
| Insecure randomness (session token) | `:68` | `random.sample(...)` builds the `SESSIONID` cookie |
| Allocation DoS | `:46` | `"#" * int(params["size"]) for _ in range(int(params["size"]))` |
| (also flagged) Command-injection demo, etc. | | |

## What this means

1. **Recall on real vulnerability classes is strong.** On DSVW, Waypoint's beacons led a verifier straight to **11 distinct real vulnerabilities** spanning SQLi, two RCE paths (pickle + exec), SSRF, XXE, command injection, weak session randomness, and a DoS — every one confirmed in the source.
2. **It finds real defects in shipping code, too.** On httpie it surfaced a genuine `verify=False` TLS-verification bug at rank #2.
3. **On mature, heavily-audited libraries it confirmed zero *new* defects — and that is the honest, expected result.** Flask, requests, werkzeug, and Django are battle-tested; their top beacons were almost all **contextual** — real risky-shaped code (pickle caches that trust a server-written store, `RawSQL`/`.extra()` that keeps user values parameterized, `exec`/`eval` in developer-only tooling, `assert` invariants) that a verifier confirms is intentional. This is the tool working as designed: **surface the shapes worth a look; the verifier decides.** It does not invent bugs in clean code.

## Precision notes — false positives worth tightening

The 27 false positives concentrate in a few identifiable rules (the value of running this loop):

- **`waypoint-py-idor-lookup-by-id` over-matches** — it fires on any `.get(key, default)` (a plain dict accessor), not just an ORM lookup of a resource by a user-supplied id. Six of the 27 FPs are this one rule (Flask `g.get`/`flash`/blueprint options, requests `LookupDict.get`, werkzeug `Authorization.parameters.get` ×2). Fix: constrain it to actual id-keyed lookups (`get(id=...)`/`get(pk=...)`/`get_object_or_404`).
- **ky's TS concurrency proxies misfire** — `waypoint-ts-shared-mutable-async` / `-shared-counter-multi-async` fired on `merge.ts` and `body.ts`, which contain **no `async`/`await` at all**, and on function-local accumulators / a per-instance `#retryCount`. ~8 of ky's 11 FPs. Fix: require a real async context **and** module-level (not local/instance) state.
- **Bandit `S104`** fires on `"0.0.0.0"` used in *string comparisons* (werkzeug log/host-allowlist branches), not actual socket binds — upstream Bandit behavior; can be down-weighted in `tag_map.yaml`.

## Reproduce

```bash
for r in <repo-paths>; do bin/wipe-beacons && bin/waypoint "$r"; done
# then open beacons/INDEX.md and verify the top entries against the source
```
Per-repo captured beacons + SARIF for this run: `hardening/results/validation/`.
