#!/usr/bin/env bash
# ============================================================================
# run_codeql.sh — the CROSS-FILE taint lane (CodeQL).
#
# Semgrep's taint mode is intraprocedural (within one function); CodeQL builds a
# whole-program database and tracks data flow ACROSS functions and files — the
# class of bug where untrusted input enters in file A and reaches a sink in file
# C, which the per-file scanners miss. It is the most expensive detector (DB
# build runs minutes+), so it is OPT-IN:
#     bin/waypoint <dir> --codeql      (or --all)
#     codeql.enabled: true  in waypoint.config.yaml   (or WAYPOINT_CODEQL=1)
#
# Emits native SARIF that merge_sarif picks up; findings are tagged by
# tag_map.yaml -> tools.codeql. Skips gracefully (with an install hint) when the
# CodeQL CLI is absent.
#
#   usage: detectors/run_codeql.sh [TARGET_DIR]
# ============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$ROOT/samples/monorepo}"
REPORTS="$ROOT/reports"; mkdir -p "$REPORTS/_codeql"
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY="$(command -v python3)"

log()  { printf '[waypoint:codeql] %s\n' "$*"; }
skip() { printf '[waypoint:codeql] SKIP %-8s — %s\n' "$1" "$2"; }
have() { command -v "$1" >/dev/null 2>&1; }
run_to() { local t="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$t" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$t" "$@"
  else "$@"; fi; }
cfg()  { "$PY" -c "import yaml; c=yaml.safe_load(open('$ROOT/waypoint.config.yaml')) or {}; v=c.get('codeql',{}).get('$1'); print(v if v is not None else '$2')" 2>/dev/null; }

# opt-in gate: WAYPOINT_CODEQL=1 forces it on; otherwise honor codeql.enabled.
ON="${WAYPOINT_CODEQL:-}"
[ -z "$ON" ] && { [ "$(cfg enabled False)" = "True" ] && ON=1 || ON=0; }
if [ "$ON" != "1" ]; then
  skip codeql "opt-in lane — pass --codeql / --all (or set codeql.enabled: true). Cross-file taint; slow."
  exit 0
fi

if ! have codeql; then
  skip codeql "CodeQL CLI not found. Install: \`gh extension install github/gh-codeql\` (then \`gh codeql\`), or download the CLI bundle from github.com/github/codeql-cli-binaries/releases and put \`codeql\` on PATH."
  exit 0
fi

CQ="$(command -v codeql)"; DBROOT="$REPORTS/_codeql"
to="$(cfg db_timeout_secs 1800)"
CQ_LANGS="$("$PY" -c "import yaml; c=yaml.safe_load(open('$ROOT/waypoint.config.yaml')) or {}; print(' '.join(c.get('codeql',{}).get('languages',['python','javascript-typescript'])))" 2>/dev/null)"
[ -n "$CQ_LANGS" ] || CQ_LANGS="python javascript-typescript"
log "target = $TARGET ; languages = $CQ_LANGS ; cli = $CQ"

n=0
for lang in $CQ_LANGS; do
  case "$lang" in
    python) suite="codeql/python-queries:codeql-suites/python-security-extended.qls" ;;
    javascript-typescript|javascript) suite="codeql/javascript-queries:codeql-suites/javascript-security-extended.qls" ;;
    *) log "no security-extended suite mapping for '$lang' — skipping"; continue ;;
  esac
  db="$DBROOT/$lang"
  log "codeql ($lang) — building database (slow; cross-file dataflow) …"
  if run_to "$to" "$CQ" database create "$db" --language="$lang" --source-root="$TARGET" --overwrite --quiet 2>/dev/null; then
    if run_to "$to" "$CQ" database analyze "$db" "$suite" --format=sarif-latest \
         --output="$REPORTS/codeql-$lang.sarif" --quiet 2>/dev/null; then
      n=$((n+1)); log "  -> reports/codeql-$lang.sarif"
    else
      log "  codeql analyze failed for $lang (is the query pack downloaded? try: codeql pack download $suite)"
    fi
  else
    log "  codeql database build failed for $lang"
  fi
done
log "done. codeql SARIF in reports/: $n file(s) (cross-file taint)"
