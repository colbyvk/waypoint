#!/usr/bin/env bash
# ============================================================================
# doctor.sh — Waypoint capability self-check. Tells you EXACTLY which detectors
# are active and what each missing one costs, so a partial install is never a
# silent surprise (an agent running Waypoint cold must know its real coverage).
#
#   detectors/doctor.sh           full report; exits 1 if the CORE is missing
#   detectors/doctor.sh --brief   one-line summary (used by the scan banner)
#
# Also surfaced as:  bin/waypoint --doctor
# ============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/.venv/bin"
BRIEF=0; [ "${1:-}" = "--brief" ] && BRIEF=1

# present in our venv, our node_modules, our .codeql, or on PATH?
_have() {
  case "$1" in
    eslint) [ -x "$ROOT/node_modules/.bin/eslint" ] ;;
    codeql) [ -x "$ROOT/.codeql/codeql/codeql" ] || command -v codeql >/dev/null 2>&1 ;;
    clippy) command -v cargo-clippy >/dev/null 2>&1 ;;
    python) [ -x "$BIN/python" ] || command -v python3 >/dev/null 2>&1 ;;
    *)      [ -x "$BIN/$1" ] || command -v "$1" >/dev/null 2>&1 ;;
  esac
}
_yn() { _have "$1" && echo 1 || echo 0; }

# --- probe once ------------------------------------------------------------
P_PY=$(_yn python);     P_SEM=$(_yn semgrep)
P_BAN=$(_yn bandit);    P_RUF=$(_yn ruff);   P_MYP=$(_yn mypy);  P_PIP=$(_yn pip-audit)
P_ESL=$(_yn eslint);    P_CLP=$(_yn clippy)
P_CA=$(_yn cargo-audit);P_CG=$(_yn cargo-geiger)
P_GL=$(_yn gitleaks);   P_TRV=$(_yn trivy);  P_OSV=$(_yn osv-scanner); P_TRF=$(_yn trufflehog)
P_CQL=$(_yn codeql)
# tree-sitter is a Python module (SOUND TS/JS/Rust call graph), not a binary:
P_TS=0; [ -x "$BIN/python" ] && "$BIN/python" -c "import tree_sitter" >/dev/null 2>&1 && P_TS=1

# CORE = a venv python + semgrep (the primary engine + all custom rules).
CORE_OK=1; { [ "$P_PY" = 1 ] && [ "$P_SEM" = 1 ]; } || CORE_OK=0

# --- brief one-liner (scan banner) -----------------------------------------
if [ "$BRIEF" = 1 ]; then
  if [ "$CORE_OK" != 1 ]; then
    echo "[waypoint] capabilities: [!] CORE MISSING (python+semgrep) — run detectors/install.sh"
    exit 1
  fi
  deg=""
  [ "$P_BAN" = 0 ] && deg="$deg bandit[--]"
  [ "$P_RUF" = 0 ] && deg="$deg ruff[--]"
  [ "$P_MYP" = 0 ] && deg="$deg mypy[--]"
  [ "$P_ESL" = 0 ] && deg="$deg eslint[--](TS/React→semgrep-only)"
  [ "$P_TS" = 0 ] && deg="$deg tree-sitter[--](TS/Rust graph regex-best-effort)"
  [ "$P_CQL" = 0 ] && deg="$deg codeql[--](no cross-file taint)"
  opt=0
  for v in "$P_PIP" "$P_CLP" "$P_CA" "$P_CG" "$P_GL" "$P_TRF" "$P_TRV" "$P_OSV"; do [ "$v" = 0 ] && opt=$((opt+1)); done
  if [ -n "$deg" ]; then
    echo "[waypoint] capabilities: core [ok] · degraded:$deg · (+$opt optional off; bin/waypoint --doctor)"
  else
    echo "[waypoint] capabilities: full Python+TS [ok] · (+$opt optional off; bin/waypoint --doctor)"
  fi
  exit 0
fi

# --- full report -----------------------------------------------------------
row() { # <0|1> <name> <what you lose if missing> <how to get it>
  if [ "$1" = 1 ]; then printf '  [ok] %-14s\n' "$2"
  else printf '  [--] %-14s %s\n      ↳ %s\n' "$2" "$3" "$4"; fi
}
echo "Waypoint capability report  ($ROOT)"
echo
echo "CORE (required to scan at all):"
row "$P_PY"  "python/.venv" "Waypoint cannot run."                 "detectors/install.sh"
row "$P_SEM" "semgrep"      "no primary engine / custom rules."    "detectors/install.sh"
echo
echo "Python depth:"
row "$P_BAN" "bandit"       "no Python security lane."             "detectors/install.sh"
row "$P_RUF" "ruff"         "no fast correctness/security lints."  "detectors/install.sh"
row "$P_MYP" "mypy"         "no type/logic (dead-code) checks."    "detectors/install.sh"
row "$P_PIP" "pip-audit"    "no Python dependency CVEs."           "detectors/install.sh"
echo
echo "Other languages:"
row "$P_ESL" "eslint"       "TypeScript/React run semgrep-only."   "detectors/install.sh --eslint"
row "$P_TS"  "tree-sitter"  "TS/JS/Rust call graph is regex-best-effort, not sound." "detectors/install.sh (auto, best-effort)"
row "$P_CLP" "clippy"       "no Rust lints."                       "rustup component add clippy"
row "$P_CA"  "cargo-audit"  "no Rust dependency advisories."       "detectors/install.sh --rust-audit"
row "$P_CG"  "cargo-geiger" "no Rust unsafe-usage report."         "detectors/install.sh --rust-audit"
echo
echo "Cross-cutting:"
row "$P_GL"  "gitleaks"     "weaker secret scanning."              "detectors/install.sh --brew"
row "$P_TRF" "trufflehog"   "no VERIFIED (live) secret detection." "detectors/install.sh --brew"
row "$P_TRV" "trivy"        "no IaC misconfig / image CVEs."       "detectors/install.sh --brew"
row "$P_OSV" "osv-scanner"  "fewer dependency CVE sources."        "detectors/install.sh --brew"
echo
echo "Deep tier (opt-in: bin/waypoint <dir> --deep/--codeql):"
row "$P_CQL" "codeql"       "no cross-file taint tracing."         "detectors/install_codeql.sh"
echo
if [ "$CORE_OK" = 1 ]; then
  echo "Verdict: [ok] ready to scan. Anything [--] above is optional — Waypoint degrades"
  echo "         gracefully, and the per-scan banner reminds you what's off."
  exit 0
else
  echo "Verdict: [!] NOT ready — the CORE is missing. Run:  detectors/install.sh"
  exit 1
fi
