#!/usr/bin/env bash
# ============================================================================
# install.sh — install Waypoint's detectors.
#
# The Python tools go in a project-local virtualenv (.venv) so they never
# collide with the system Python (modern macOS/Homebrew Python is
# externally-managed — PEP 668 — and refuses global pip installs).
#
#   detectors/install.sh              # Python tools + Rust clippy (fast, default)
#   detectors/install.sh --rust-audit # also cargo-audit + cargo-geiger (slow build)
#   detectors/install.sh --eslint     # also Waypoint-OWNED eslint stack (into waypoint/node_modules)
#   detectors/install.sh --brew       # also gitleaks + trivy + osv-scanner
#   detectors/install.sh --all        # everything
#
# Note: ESLint is installed into WAYPOINT's own node_modules (not the scanned
# project's) on purpose — run_all.sh never executes the target's eslint binary,
# config, or plugins (all attacker-controlled code). CodeQL: detectors/install_codeql.sh.
#
# Everything is open source; nothing here is reimplemented (spec §13).
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WANT_RUST_AUDIT=0; WANT_BREW=0; WANT_ESLINT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --rust-audit)   WANT_RUST_AUDIT=1 ;;
    --brew)         WANT_BREW=1 ;;
    --eslint|--node) WANT_ESLINT=1 ;;
    --all)          WANT_RUST_AUDIT=1; WANT_BREW=1; WANT_ESLINT=1 ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac; shift
done
log() { printf '[install] %s\n' "$*"; }

# --- Python tools in a venv (always; this is the CORE — fail loudly) --------
log "creating virtualenv .venv (if missing) and installing Python detectors"
command -v python3 >/dev/null 2>&1 || { echo "[install] FATAL: python3 not found on PATH — install Python 3 first."; exit 1; }
[ -d .venv ] || python3 -m venv .venv || { echo "[install] FATAL: could not create .venv"; exit 1; }
.venv/bin/python -m pip install --quiet --upgrade pip || { echo "[install] FATAL: pip upgrade failed in .venv"; exit 1; }
.venv/bin/python -m pip install --quiet -r "$ROOT/requirements.txt" || {
  echo "[install] FATAL: core Python detectors failed to install (see pip output above)."
  echo "[install]        Waypoint cannot scan without them — fix the error and re-run."
  exit 1; }
log "Python detectors installed from requirements.txt (pinned versions)"

# --- tree-sitter: SOUND call graph for TS/JS/Rust (best-effort, default-on) -----
# Installed separately so a missing wheel degrades the clike graph to the regex
# extractor (graceful) instead of breaking the core install. Python uses ast.
if .venv/bin/python -m pip install --quiet -r "$ROOT/requirements-treesitter.txt" 2>/dev/null; then
  log "tree-sitter installed — TS/JS/Rust call graph is SOUND"
else
  log "tree-sitter unavailable for this platform — TS/JS/Rust call graph stays regex-best-effort (Python is still sound)"
fi

# --- Rust: clippy component (fast) -----------------------------------------
if command -v rustup >/dev/null 2>&1; then
  log "adding rustup clippy component"
  rustup component add clippy >/dev/null 2>&1 || log "  (clippy add failed — check rustup)"
else
  log "rustup not found — skipping Rust clippy (install rustup to enable)"
fi

# --- Rust advisory tools (optional, slow to build) -------------------------
if [ "$WANT_RUST_AUDIT" = 1 ] && command -v cargo >/dev/null 2>&1; then
  log "cargo install cargo-audit cargo-geiger (this compiles from source; slow)"
  cargo install cargo-audit  --locked >/dev/null 2>&1 || log "  cargo-audit install failed"
  cargo install cargo-geiger --locked >/dev/null 2>&1 || log "  cargo-geiger install failed"
fi

# --- ESLint stack, WAYPOINT-OWNED (optional) -------------------------------
# Installs into waypoint/node_modules so run_all.sh runs OUR eslint with OUR
# config — never the scanned project's binary/config/plugins (code-exec risk).
if [ "$WANT_ESLINT" = 1 ] && command -v npm >/dev/null 2>&1; then
  log "installing Waypoint-owned ESLint stack from package-lock.json (npm ci, reproducible)"
  ( cd "$ROOT" && npm ci --silent --no-audit --no-fund ) || log "  npm ci failed (try: cd waypoint && npm ci)"
fi

# --- Cross-cutting via Homebrew (optional) ---------------------------------
if [ "$WANT_BREW" = 1 ] && command -v brew >/dev/null 2>&1; then
  log "brew install gitleaks trivy osv-scanner trufflehog"
  brew install gitleaks trivy osv-scanner trufflehog >/dev/null 2>&1 || log "  brew install partial/failed"
fi

cat <<'EOF'

[install] CodeQL (cross-file taint — the deep tier) is a large separate
  toolchain, not installed above. Add it with one verified command:
    detectors/install_codeql.sh    (then: bin/waypoint <dir> --codeql)
EOF
echo
log "capability report (what's active, and what each gap costs):"
echo
bash "$ROOT/detectors/doctor.sh" || true
