# Changelog

All notable changes to Waypoint. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versioning is [SemVer](https://semver.org/).

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
- **Taint-mode Semgrep rules** (`infra/<lang>/security/*-taint.yaml`) — free intra-file
  source→sink dataflow (command/SQL/SSRF/code/deser/SSTI/path/XSS/redirect), with a
  regression test pinning the PLANT/OK fixture contract.
- **TruffleHog verified-secrets lane** (opt-in) — confirms a credential is live
  (high precision over regex); JSONL→SARIF, secret value never written.
- **Registry packs** via `SEMGREP_EXTRA` (no new dependency).

### Quality & proof
- **103 tests** (no external scanner required); CI cold-installs and self-tests on
  fresh Ubuntu + macOS across Python 3.11/3.12.
- Security hardening: config isolation, gated/sandboxed dynamic lanes, verified CodeQL
  download, secret redaction, path containment (see [SECURITY.md](SECURITY.md)).
- Validated on real repos — DSVW, requests, itsdangerous, ky, **werkzeug**, **django**
  (165k LOC in ~73s). See `hardening/RESULTS.md` and `hardening/PROOF.md`.

[0.1.0]: https://github.com/colbyvk/waypoint/releases/tag/v0.1.0
