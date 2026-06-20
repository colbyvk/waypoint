#!/usr/bin/env bash
# ============================================================================
# run_logic.sh — the software-LOGIC testing lane (spec extension).
#
# Static rules flag the *shape* of a logic hazard; this lane brings DYNAMIC
# evidence — surviving mutants, observed data races, fuzz crashes — and turns
# each into a `logic` beacon that merges/ranks/dispatches with everything else.
# So a region a static concurrency rule flagged can arrive at the agent WITH a
# race-detector hit attached.
#
# It is SLOW (mutation testing re-runs your suite per mutant; fuzzing runs for
# minutes+), so it is OPT-IN and belongs in a nightly lane, not per-PR:
#     logic.enabled: true   in waypoint.config.yaml   (or WAYPOINT_LOGIC=1)
# `bin/waypoint <dir> --logic` forces it on.
#
#   usage: detectors/run_logic.sh [TARGET_DIR]
# ============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$ROOT/samples/monorepo}"
REPORTS="$ROOT/reports"; NORM="$ROOT/detectors/normalize"
mkdir -p "$REPORTS/_work"
# Keep the scanned tree pristine — build artifacts go to reports/_work, never the target.
export CARGO_TARGET_DIR="$REPORTS/_work/cargo-target"
BIN="$ROOT/.venv/bin"; PY="$BIN/python"; [ -x "$PY" ] || PY="$(command -v python3)"

log()  { printf '[waypoint:logic] %s\n' "$*"; }
skip() { printf '[waypoint:logic] SKIP %-14s — %s\n' "$1" "$2"; }
have() { [ -x "$BIN/$1" ] || command -v "$1" >/dev/null 2>&1; }
run_to() { local t="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$t" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$t" "$@"
  else "$@"; fi; }
cfg() { "$PY" -c "import yaml,sys; c=yaml.safe_load(open('$ROOT/waypoint.config.yaml')) or {}; v=c.get('logic',{}).get('$1'); print(v if v is not None else '$2')" 2>/dev/null; }

LOGIC_ON="${WAYPOINT_LOGIC:-}"
[ -z "$LOGIC_ON" ] && { [ "$(cfg enabled False)" = "True" ] && LOGIC_ON=1 || LOGIC_ON=0; }
if [ "$LOGIC_ON" != "1" ]; then
  skip logic "opt-in lane — set logic.enabled: true or WAYPOINT_LOGIC=1 (slow; nightly)"
  exit 0
fi
# This lane EXECUTES the target's own code (cargo test, pytest, fuzzers). Refuse
# unless explicitly trusted (bin/waypoint sets this after --i-trust-this-code).
if [ "${WAYPOINT_TRUSTED:-}" != "1" ]; then
  skip logic "runs the TARGET's own code — set WAYPOINT_TRUSTED=1 (bin/waypoint --i-trust-this-code) or use bin/waypoint-sandboxed"
  exit 0
fi
log "target = $TARGET"

# --------------------------------------------------------------------------- #
# 1) Mutation testing — cargo-mutants on each Rust crate. Surviving mutants =
#    test gaps / possible logic bugs. (Turnkey; slow.)
# --------------------------------------------------------------------------- #
if [ "$(cfg mutants True)" = "True" ] && have cargo-mutants; then
  to="$(cfg mutants_timeout_secs 1200)"
  i=0
  while IFS= read -r manifest; do
    crate="$(dirname "$manifest")"; i=$((i+1))
    log "cargo-mutants ($crate) — slow; re-runs the suite per mutant"
    ( cd "$crate" && run_to "$to" cargo mutants --output "$REPORTS/_work/mutants-$i" 2>/dev/null ) || true
    oc="$REPORTS/_work/mutants-$i/outcomes.json"
    [ -f "$oc" ] && "$PY" "$NORM/mutants_to_sarif.py" "$oc" -o "$REPORTS/mutants-$i.sarif"
  done < <(find "$TARGET" -name Cargo.toml -not -path '*/target/*' 2>/dev/null)
else
  skip cargo-mutants "cargo install cargo-mutants (or logic.mutants: false)"
fi

# --------------------------------------------------------------------------- #
# 2) Ingest race-detector reports (Go `-race`, ThreadSanitizer) that your test
#    lane already produces. Configure logic.race_reports (globs, relative to the
#    target) or set WAYPOINT_RACE_REPORT.
# --------------------------------------------------------------------------- #
ingest() {  # $1=normalizer  $2=glob-list-csv  $3=out-prefix  $4=env-extra
  local norm="$1" globs="$2" prefix="$3" extra="$4" n=0
  for g in ${globs//,/ } $extra; do
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      n=$((n+1)); "$PY" "$NORM/$norm" "$f" -o "$REPORTS/$prefix-$n.sarif"
    done < <(compgen -G "$TARGET/$g" 2>/dev/null; compgen -G "$g" 2>/dev/null)
  done
  [ "$n" = 0 ] && skip "$prefix" "no reports matched (configure logic.${prefix}_reports)"
}
ingest race_to_sarif.py "$(cfg race_reports '')" race "${WAYPOINT_RACE_REPORT:-}"
ingest fuzz_to_sarif.py "$(cfg fuzz_reports '')" fuzz "${WAYPOINT_FUZZ_REPORT:-}"

# --------------------------------------------------------------------------- #
# 3) Property-based testing — assert INVARIANTS over generated inputs; a failure
#    shrinks to a MINIMAL counterexample that becomes a `logic` beacon carrying
#    the reproducing input. Finds correctness bugs with NO spec and NO existing
#    tests. Per language: Hypothesis (Py), proptest/quickcheck (Rust),
#    fast-check (TS/React). Best-effort: each sub-lane skips cleanly if its
#    toolchain or a runnable harness is absent.
# --------------------------------------------------------------------------- #
if [ "$(cfg property True)" = "True" ]; then
  pto="$(cfg property_timeout_secs 300)"

  # Python — Hypothesis. Run existing property tests, and (optionally) auto-write
  # new ones with the ghostwriter for modules that have none (the "vibe code has
  # no tests" bridge), then run those too.
  if "$PY" -c 'import hypothesis' 2>/dev/null; then
    pout="$REPORTS/_work/hypothesis.out"; : > "$pout"
    if "$PY" -c 'import pytest' 2>/dev/null; then
      run_to "$pto" "$PY" -m pytest -q -p no:cacheprovider -k "property or hypothesis" \
        "$TARGET" >>"$pout" 2>&1 || true
    fi
    if [ "$(cfg property_generate True)" = "True" ]; then
      gendir="$REPORTS/_work/hypothesis-gen"; mkdir -p "$gendir"
      while IFS= read -r mod; do
        rel="${mod#"$TARGET"/}"; dotted="${rel%.py}"; dotted="${dotted//\//.}"
        name="${dotted//./_}"
        ( cd "$TARGET" && PYTHONPATH="$TARGET" run_to 60 "$PY" -m hypothesis write "$dotted" ) \
          > "$gendir/test_${name}.py" 2>/dev/null || true
        [ -s "$gendir/test_${name}.py" ] || rm -f "$gendir/test_${name}.py"
      done < <(find "$TARGET" -name '*.py' -not -path '*/.venv/*' -not -path '*/tests/*' \
                 -not -name 'test_*' 2>/dev/null | head -30)
      # differential / metamorphic relations — generate with the ghostwriter's
      # relation modes (--roundtrip / --idempotent / --equivalent / --binary-op).
      "$PY" -c "import yaml; c=yaml.safe_load(open('$ROOT/waypoint.config.yaml')) or {}; [print(x) for x in (c.get('logic',{}).get('property_relations') or [])]" 2>/dev/null \
        | while IFS= read -r spec; do
            [ -n "$spec" ] || continue
            ( cd "$TARGET" && PYTHONPATH="$TARGET" run_to 60 "$PY" -m hypothesis write $spec ) \
              >> "$gendir/test_relations.py" 2>/dev/null || true
          done
      if [ -n "$(ls -A "$gendir" 2>/dev/null)" ]; then
        run_to "$pto" "$PY" -m pytest -q -p no:cacheprovider "$gendir" >>"$pout" 2>&1 || true
      fi
    fi
    [ -s "$pout" ] && "$PY" "$NORM/hypothesis_to_sarif.py" "$pout" -o "$REPORTS/hypothesis.sarif"
  else
    skip hypothesis "pip install hypothesis (Python property-based testing)"
  fi

  # Rust — proptest / quickcheck run under `cargo test`.
  if have cargo; then
    i=0
    while IFS= read -r manifest; do
      crate="$(dirname "$manifest")"; i=$((i+1))
      ( cd "$crate" && run_to "$pto" cargo test 2>&1 ) > "$REPORTS/_work/proptest-$i.out" 2>&1 || true
      [ -s "$REPORTS/_work/proptest-$i.out" ] && \
        "$PY" "$NORM/proptest_to_sarif.py" "$REPORTS/_work/proptest-$i.out" -o "$REPORTS/proptest-$i.sarif"
    done < <(find "$TARGET" -name Cargo.toml -not -path '*/target/*' 2>/dev/null)
  else
    skip proptest "rustup/cargo not found (Rust property-based testing)"
  fi

  # TypeScript / React — fast-check runs under the project's test runner.
  if have npx && [ -f "$TARGET/package.json" ]; then
    ( cd "$TARGET" && run_to "$pto" npx --no-install jest 2>&1 \
        || run_to "$pto" npx --no-install vitest run 2>&1 ) \
      > "$REPORTS/_work/fastcheck.out" 2>&1 || true
    [ -s "$REPORTS/_work/fastcheck.out" ] && \
      "$PY" "$NORM/fastcheck_to_sarif.py" "$REPORTS/_work/fastcheck.out" -o "$REPORTS/fastcheck.sarif"
  else
    skip fast-check "npx + package.json needed (TS/React property-based testing)"
  fi

  # Pre-saved property-test logs (each normalizer only fires on its own format).
  pr=0
  for g in $(cfg property_reports '' | tr ',' ' ') ${WAYPOINT_PROPERTY_REPORT:-}; do
    while IFS= read -r f; do
      [ -f "$f" ] || continue; pr=$((pr+1))
      for n in hypothesis_to_sarif proptest_to_sarif fastcheck_to_sarif; do
        "$PY" "$NORM/$n.py" "$f" -o "$REPORTS/property-$pr-$n.sarif" 2>/dev/null || true
      done
    done < <(compgen -G "$TARGET/$g" 2>/dev/null; compgen -G "$g" 2>/dev/null)
  done
fi

# --------------------------------------------------------------------------- #
# 4) Fuzzing — coverage-guided input generation that drives the code into a
#    crash/panic/hang; the offending input rides on the beacon. Per language:
#    cargo-fuzz (Rust), atheris (Python), jazzer.js (TS/JS). Opt-in + slow.
# --------------------------------------------------------------------------- #
if [ "$(cfg fuzz True)" = "True" ]; then
  fsecs="$(cfg fuzz_secs 60)"

  if have cargo-fuzz; then
    while IFS= read -r ftd; do
      crate="$(cd "$(dirname "$ftd")/.." && pwd 2>/dev/null || echo "$ftd")"
      while IFS= read -r t; do
        tn="$(basename "$t" .rs)"
        ( cd "$crate" && run_to "$fsecs" cargo fuzz run "$tn" -- -max_total_time="$fsecs" 2>&1 ) \
          > "$REPORTS/_work/cargofuzz-$tn.out" 2>&1 || true
        [ -s "$REPORTS/_work/cargofuzz-$tn.out" ] && \
          "$PY" "$NORM/fuzz_to_sarif.py" "$REPORTS/_work/cargofuzz-$tn.out" -o "$REPORTS/fuzz-rs-$tn.sarif" || true
      done < <(find "$ftd" -name '*.rs' 2>/dev/null)
    done < <(find "$TARGET" -type d -name fuzz_targets 2>/dev/null)
  else
    skip cargo-fuzz "cargo install cargo-fuzz (Rust fuzzing)"
  fi

  if "$PY" -c 'import atheris' 2>/dev/null; then
    while IFS= read -r h; do
      hn="$(basename "$h" .py)"
      ( cd "$(dirname "$h")" && run_to "$fsecs" "$PY" "$h" -max_total_time="$fsecs" 2>&1 ) \
        > "$REPORTS/_work/atheris-$hn.out" 2>&1 || true
      [ -s "$REPORTS/_work/atheris-$hn.out" ] && \
        "$PY" "$NORM/fuzz_to_sarif.py" "$REPORTS/_work/atheris-$hn.out" -o "$REPORTS/fuzz-py-$hn.sarif" || true
    done < <(grep -rl 'atheris' "$TARGET" --include='*_fuzz.py' 2>/dev/null)
  else
    skip atheris "pip install atheris (Python fuzzing)"
  fi

  if have npx; then
    while IFS= read -r h; do
      hn="$(basename "$h" | tr './' '__')"
      ( cd "$TARGET" && run_to "$fsecs" npx --no-install jazzer "$h" -- -max_total_time="$fsecs" 2>&1 ) \
        > "$REPORTS/_work/jazzer-$hn.out" 2>&1 || true
      [ -s "$REPORTS/_work/jazzer-$hn.out" ] && \
        "$PY" "$NORM/fuzz_to_sarif.py" "$REPORTS/_work/jazzer-$hn.out" -o "$REPORTS/fuzz-js-$hn.sarif" || true
    done < <(find "$TARGET" \( -name '*.fuzz.ts' -o -name '*.fuzz.js' \) 2>/dev/null)
  else
    skip jazzer "npx needed for jazzer.js (TS/JS fuzzing)"
  fi
fi

n_logic=$(ls "$REPORTS"/mutants-*.sarif "$REPORTS"/race-*.sarif "$REPORTS"/fuzz-*.sarif \
             "$REPORTS"/hypothesis*.sarif "$REPORTS"/proptest-*.sarif "$REPORTS"/fastcheck*.sarif \
             "$REPORTS"/property-*.sarif 2>/dev/null | wc -l | tr -d ' ')
log "done. logic SARIF in reports/: $n_logic file(s) (mutants · race · fuzz · property)"
