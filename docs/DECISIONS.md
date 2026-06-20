# Decisions left to the owner (spec §15)

These five choices are deliberately **not guessed**. Each has a working default so
the system runs today; this is where you change them.

---

### 1. Repo hosting (GitHub / GitLab / other)

Affects CodeQL setup and the SARIF-upload step.

- **Default:** GitHub. `.github/workflows/waypoint.yml` uploads SARIF via
  `github/codeql-action/upload-sarif@v3` to the Security tab.
- **GitLab:** drop the upload step and instead publish `reports/ranked.sarif` as a
  [SAST report artifact](https://docs.gitlab.com/ee/user/application_security/sast/).
  The detector/merge/rank stages are host-agnostic.

---

### 2. Which model backs the agent, and the per-run budget

- **Default model:** `claude-opus-4-8` (`waypoint.config.yaml` → `dispatch.model`).
- **Default budget:** top **25** ranked beacons per run (`dispatch.budget_top_n`).
  This is the single biggest cost lever — raise it for thoroughness, lower it to
  save money. PRs get *all* the cheap deterministic beacons regardless; the budget
  only caps how many get an agent visit.
- **Default backend:** `dry-run` (writes prompts, calls no model). Switch to
  `anthropic-api` or `claude-cli` (or RAPTOR) when you are ready to spend.

---

### 3. Whether CodeQL runs at all

CodeQL is the one true cross-file taint tracer, but the most expensive piece (a DB
build can take tens of minutes).

- **Now: ON** (owner enabled). `waypoint.config.yaml` → `codeql.enabled: true`,
  `languages: [python, javascript-typescript]`, and `codeql` is in
  `detectors.cross`. `run_all.sh` builds a CodeQL database per language and runs
  the `*-security-extended` query suite, emitting native SARIF that merges like
  any other beacon source.
- **Requires the CodeQL CLI on PATH.** It is large and not bundled; install from
  <https://github.com/github/codeql-cli-binaries>. When the CLI is absent the step
  logs a SKIP and the rest of the pipeline runs unchanged (so CI without CodeQL
  still works). DB builds can take minutes+ — that cost is why it stays config-gated.
- Treat CodeQL path results as high-confidence beacons; pair with RAPTOR's
  path-satisfiability gating (`dispatch/raptor/`) so unreachable paths don't spend
  an agent call.

---

### 4. Suppression expiry window, and allowlist sign-off

- **Default expiry:** **90 days** (`suppression.default_expiry_days`). After that a
  dismissed region is re-examined even if unchanged. Shorten for higher-assurance
  code; lengthen for stable legacy.
- **Allowlist:** every `suppression/allowlist.yaml` entry already *requires* a
  justification and an expiry (rank.py reports and ignores entries missing either).
  Whether a human must **sign off** (e.g. CODEOWNERS review on that file) is a
  process choice — recommended: protect `suppression/allowlist.yaml` with a
  required reviewer. The content-hash store is agent-written and needs no sign-off.

---

### 5. Monorepo vs per-service invocation, and how centrality is computed

- **Default:** whole-tree. `run_all.sh <dir>` scans one tree; centrality counts
  call sites of a region's enclosing symbol across that tree
  (`prioritise/rank.py`, an intentionally rough approximation — spec §7).
- **Per-service:** run the pipeline per service directory and merge the resulting
  beacon files, or pass each service as a separate `WAYPOINT_TARGET`. Per-service
  invocation makes centrality local to the service (usually what you want — a
  symbol's callers inside its own service matter more than incidental name
  collisions across the monorepo).
- The caller-count heuristic is name-based and approximate by design. If you need
  precision later, swap `build_corpus`/`caller_count` in `rank.py` for a real call
  graph (tree-sitter or each language's own tooling) — nothing else changes.
