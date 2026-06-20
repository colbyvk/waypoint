# Changelog

All notable changes to Waypoint. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

## [Unreleased]

### Changed
- **Repositioned as a tool, not an agentic harness.** Waypoint runs no model and
  **needs no API key** for anything it's for — the agent (or human) that *drives* it
  reads the beacons and verifies them. Reframed the README top + flow diagram, the
  SKILL guide, `docs/DECISIONS`, `bin/waypoint --help`, and the dispatcher to lead
  with this. The optional `--dispatch`/`--investigate` model backends are demoted to a
  clearly-labeled "headless, no agent present" escape hatch — the sole place a key is
  ever used, and never required; `dry-run` (write prompts, no model, no key) stays the
  default. The example CI (`.github/workflows/waypoint.yml`) now runs **key-free**; its
  model-calling triage job ships commented-out. No behavior change — framing only.

### Fixed
- **`waypoint-py-thread-shared-mutable-nolock` was over-broad.** Its `$G` guard
  (`^(?!self$).+`) excluded only the bare name `self`, so it fired on local
  variables, function parameters, and `self.attr[...]` — not the module-level
  shared state it targets. On Flask it produced **117 of 221 beacons (53%)**,
  effectively all false positives. It now enforces the module-global convention
  the rule already documented (`$G` is UPPER_CASE, optionally `_`-prefixed).
  Result: Flask **221 → 95 beacons**, concurrency axis **118 → 0**, with the
  PLANT fixture still firing (zero recall loss). The over-broad-proxy lesson: a
  recall-biased rule still has to encode *some* evidence of its target.

### Validated
- Fresh end-to-end runs on **Flask** (9.5k LOC, 9s) and **httpie** (9.8k LOC, 4s);
  the coverage partition holds on both. The httpie run surfaced a genuine
  `requests.get(..., verify=False)` (TLS verification disabled) in its production
  update check, ranked **#2**. See `hardening/proof_flask/` + `hardening/proof_httpie/`.

## [0.1.0] — 2026-06-20

First public release.

### Core
- **Tiered CLI** (`bin/waypoint`): `fast` (default — static, `$0`, seconds, no target
  code executed) → `--changed` (incremental vs git) → `--deep` (CodeQL cross-file taint
  + dynamic logic lane) → `--dispatch` / `--investigate` (agent verifies the top-N).
- **176 custom rules** across **Python · Rust · TypeScript · React** and five axes
  (security · edge-case · concurrency · abuse · logic), plus wired off-the-shelf
  scanners (Semgrep, Bandit, Ruff, mypy, Clippy, Trivy, Gitleaks, pip-audit,
  osv-scanner, ESLint) and optional CodeQL.
- **SARIF beacons** — one universal format, no custom schema; merged, deduped,
  ranked, suppressible.
- **Real call-graph ranking** (distinct-caller fan-in + proven boundary reachability)
  and a per-rule **precision calibration** loop from agent/human verdicts.

### The dark zone
- Every scan emits `beacons/BLINDSPOTS.md` — the regions the static pass **could not
  verify** (dynamic dispatch, reflection, framework-reached handlers, unparsed files).
  `--investigate` sends the observed-adjacent ones to an LLM with a scoped question each.
- **Honest + sound dark zone:** gaps are tiered by **observed facts only** (code-exec-
  adjacent > sink-adjacent > opaque > unparsed) with reachability marked `UNRESOLVED` —
  **no fabricated severity** for regions we didn't traverse; opaque/unparsed are counted,
  never graded. And a **coverage partition** is asserted every run — `analyzed ∪ dark =
  all enumerated functions`, with a conservative call graph (unresolved/un-boundable edges
  never mark a target reachable). See **GUARANTEES.md** for the honest guarantee ladder.

### Distribution
- **MCP server** (`integrations/mcp/waypoint_mcp.py`, `bin/waypoint-mcp`) — any MCP
  agent drives Waypoint via `waypoint_doctor/scan/beacons/dark_zone`. Claude Code
  plugin (`.claude-plugin/plugin.json`) + project `.mcp.json`.
- **`bin/waypoint --doctor`** capability self-check + a one-line banner on every scan,
  so a partial install is never silent. `install.sh` fails loudly on the core.
- **Human-output cap**: `beacons/INDEX.md` shows the top-N (config `emit.top_n`); the
  full ranked set stays in `reports/ranked.sarif`.

### Soundness & depth
- **Sound call graph via tree-sitter** for TS/JS/TSX/JSX/Rust (Python stays on `ast`):
  real grammars → sound syntactic enumeration + reliable bodies (ERROR/MISSING →
  `parse-incomplete`, dark). Optional + graceful regex fallback; `--doctor` reports the
  backend. The coverage frontier is now uniform, not Python-only.
- **Taint-mode Semgrep rules** (`infra/core/<lang>/security/*-taint.yaml`) — free intra-file
  source→sink dataflow (command/SQL/SSRF/code/deser/SSTI/path/XSS/redirect), with a
  regression test pinning the PLANT/OK fixture contract.
- **TruffleHog verified-secrets lane** (opt-in) — confirms a credential is live
  (high precision over regex); JSONL→SARIF, secret value never written.
- **Registry packs** via `SEMGREP_EXTRA` (no new dependency).

### Quality & proof
- **112 tests** (no external scanner required); CI cold-installs and self-tests on
  fresh Ubuntu + macOS across Python 3.11/3.12.
- Security hardening: config isolation, gated/sandboxed dynamic lanes, verified CodeQL
  download, secret redaction, path containment (see [SECURITY.md](SECURITY.md)).
- Validated on real repos — DSVW, requests, itsdangerous, ky, **werkzeug**, **django**
  (165k LOC in ~73s). See `hardening/RESULTS.md` and `hardening/PROOF.md`.

[0.1.0]: https://github.com/colbyvk/waypoint/releases/tag/v0.1.0
