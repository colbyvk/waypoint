#!/usr/bin/env bash
# ============================================================================
# run_all.sh — run every configured detector and emit one SARIF file per tool
# into reports/. Tools that are not installed are SKIPPED (logged), so the
# pipeline always degrades gracefully. This stage has NO AI in it.
#
#   usage: detectors/run_all.sh [TARGET_DIR]
#          TARGET_DIR defaults to samples/monorepo (the bundled test fixture).
#
# Output: reports/<tool>.sarif  (raw, per-tool — the auditable "what fired"
# record, spec §2.3). Merge them with detectors/merge_sarif.py.
# ============================================================================
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-$ROOT/samples/monorepo}"
REPORTS="$ROOT/reports"
NORM="$ROOT/detectors/normalize"
mkdir -p "$REPORTS"

# Keep the SCANNED TREE pristine. Waypoint never edits source, and we redirect
# every tool cache / build artifact into reports/_work (gitignored) so a scan of
# someone's repo never litters it with target/, .mypy_cache, .ruff_cache, etc.
export MYPY_CACHE_DIR="$REPORTS/_work/mypy_cache"
export RUFF_CACHE_DIR="$REPORTS/_work/ruff_cache"
export CARGO_TARGET_DIR="$REPORTS/_work/cargo-target"
mkdir -p "$REPORTS/_work"

# Prefer tools from the project venv; fall back to PATH.
BIN="$ROOT/.venv/bin"
PY="$BIN/python"; [ -x "$PY" ] || PY="$(command -v python3)"

log()  { printf '[waypoint] %s\n' "$*"; }
skip() { printf '[waypoint] SKIP %-13s — %s\n' "$1" "$2"; }
# tool present? checks venv bin first, then PATH
have() { [ -x "$BIN/$1" ] || command -v "$1" >/dev/null 2>&1; }
bin()  { if [ -x "$BIN/$1" ]; then echo "$BIN/$1"; else command -v "$1"; fi; }
relpath() { "$PY" -c "import os,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))" "$1" "$2"; }
# portable timeout: coreutils `timeout`/`gtimeout` if present (Linux/CI), else run
# directly (macOS has neither by default — using `timeout` there aborts the call).
run_to() { local t="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$t" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$t" "$@"
  else "$@"; fi; }

# ---- incremental (changed-files) scoping ------------------------------------
# Full scan: every tool runs over $TARGET. Changed-mode (WAYPOINT_FILES = a file
# listing changed paths): the per-file scanners run ONLY over those files
# (semgrep is the bottleneck — this is the speed lever) and the
# repo/crate/manifest-level scanners skip (a baseline cache covers the rest).
CHANGED=0
SEMGREP_TARGETS=("$TARGET"); PY_TARGETS=("$TARGET"); TS_TARGETS=("$TARGET")
if [ -n "${WAYPOINT_FILES:-}" ] && [ -s "${WAYPOINT_FILES:-/dev/null}" ]; then
  CHANGED=1
  # NUL-delimited in and out, so filenames with spaces/newlines survive.
  _filt() { "$PY" - "$WAYPOINT_FILES" "$@" <<'PYEOF'
import sys
lf, *exts = sys.argv[1:]; exts = tuple("." + e for e in exts)
for p in open(lf, "rb").read().split(b"\0"):
    s = p.decode("utf-8", "replace").strip()
    if s and s.endswith(exts):
        sys.stdout.write(s + "\0")
PYEOF
}
  SEMGREP_TARGETS=(); while IFS= read -r -d '' f; do [ -n "$f" ] && SEMGREP_TARGETS+=("$f"); done < <(_filt py rs ts tsx js jsx)
  PY_TARGETS=();      while IFS= read -r -d '' f; do [ -n "$f" ] && PY_TARGETS+=("$f"); done < <(_filt py)
  TS_TARGETS=();      while IFS= read -r -d '' f; do [ -n "$f" ] && TS_TARGETS+=("$f"); done < <(_filt ts tsx js jsx)
  log "changed-mode: ${#SEMGREP_TARGETS[@]} changed source file(s); repo-level scanners skip"
fi

log "target = $TARGET"
log "clearing old per-tool SARIF in reports/"
rm -f "$REPORTS"/*.sarif

# --------------------------------------------------------------------------- #
# Semgrep — primary beacon source + ALL custom Waypoint rules (py/rust/ts/react).
# Run once over the whole target. We use --json (not --sarif) because Semgrep's
# SARIF exporter drops our custom metadata; the normalizer restores it.
# Extra registry packs can be added via:  SEMGREP_EXTRA="p/python p/react"
# --------------------------------------------------------------------------- #
if [ "$CHANGED" = 1 ] && [ ${#SEMGREP_TARGETS[@]} -eq 0 ]; then
  skip semgrep "changed-mode: no changed source files"
elif have semgrep; then
  log "semgrep (custom rules${SEMGREP_EXTRA:+ + $SEMGREP_EXTRA})"
  # Pass 1 — the python/rust/typescript rule packs over ALL changed/target files.
  # React is intentionally EXCLUDED here and run separately below: its rules are
  # languages:[typescript], so applied to ordinary .ts modules they misfire (e.g.
  # the "direct state mutation" proxy `$X.$F = $V` matches any `obj.field = x`).
  cfg=(--config "$ROOT/infra/python" --config "$ROOT/infra/rust" --config "$ROOT/infra/typescript")
  for extra in ${SEMGREP_EXTRA:-}; do cfg+=(--config "$extra"); done
  "$(bin semgrep)" "${cfg[@]}" "${SEMGREP_TARGETS[@]}" --json --output "$REPORTS/_semgrep.json" \
     --no-git-ignore --metrics=off --quiet 2>/dev/null || true
  "$PY" "$NORM/semgrep_to_sarif.py" "$REPORTS/_semgrep.json" -o "$REPORTS/semgrep.sarif"
  # Pass 2 — React rules, scoped to React component files (*.tsx/*.jsx) via
  # --include so they never fire on plain TypeScript logic.
  log "semgrep (react rules, *.tsx/*.jsx only)"
  "$(bin semgrep)" --config "$ROOT/infra/react" "${SEMGREP_TARGETS[@]}" \
     --include '*.tsx' --include '*.jsx' --json --output "$REPORTS/_semgrep_react.json" \
     --no-git-ignore --metrics=off --quiet 2>/dev/null || true
  [ -s "$REPORTS/_semgrep_react.json" ] && \
    "$PY" "$NORM/semgrep_to_sarif.py" "$REPORTS/_semgrep_react.json" -o "$REPORTS/semgrep-react.sarif"
else
  skip semgrep "pip install semgrep (see detectors/install.sh)"
fi

# --------------------------------------------------------------------------- #
# Python: bandit, ruff (native SARIF), mypy, pip-audit
# --------------------------------------------------------------------------- #
if [ "$CHANGED" = 1 ] && [ ${#PY_TARGETS[@]} -eq 0 ]; then
  skip bandit "changed-mode: no changed Python files"
elif have bandit; then
  log "bandit"
  # Skip B101 (assert_used): a LOW-severity informational check that fires on
  # every assert — overwhelmingly test code. As a triage beacon it is near-zero
  # signal (measured: 574 B101 hits in one real repo's tests). Real hardcoded-cred
  # checks (B105-B107) stay on; test instances of those are sunk by rank.py.
  if [ "$CHANGED" = 1 ]; then
    "$(bin bandit)" "${PY_TARGETS[@]}" -s B101 -f json -o "$REPORTS/_bandit.json" --quiet 2>/dev/null || true
  else
    "$(bin bandit)" -r "$TARGET" -s B101 -f json -o "$REPORTS/_bandit.json" --quiet 2>/dev/null || true
  fi
  "$PY" "$NORM/bandit_to_sarif.py" "$REPORTS/_bandit.json" -o "$REPORTS/bandit.sarif"
else
  skip bandit "pip install bandit"
fi

if [ "$CHANGED" = 1 ] && [ ${#PY_TARGETS[@]} -eq 0 ]; then
  skip ruff "changed-mode: no changed Python files"
elif have ruff; then
  log "ruff (native SARIF)"
  # Select the families that map to Waypoint axes — recall over precision, since
  # beacons are deduped/ranked/suppressible and the agent does the real judging:
  #   E,F correctness · B bugbear · S flake8-bandit (security) · ASYNC concurrency
  #   BLE blind-except · DTZ naive-datetime · PERF perf/amplification · TRY except-flow
  # Ignore line-length and the chatty TRY003. Overlaps with Bandit dedup downstream.
  # --config pins OUR ruff settings (selection + test-file ignores) so the scanned
  # project's ruff config is never read — same isolation as mypy's --config-file.
  # The config silences test-only noise (asserts/fixture-creds/seeded-RNG) in test
  # files; measured to remove ~575 S101 false positives from one real test suite.
  "$(bin ruff)" check "${PY_TARGETS[@]}" --config "$ROOT/infra/ruff/waypoint.toml" \
     --output-format sarif > "$REPORTS/ruff.sarif" 2>/dev/null || true
  # ruff writes a valid empty SARIF even with findings; if it wrote nothing, drop it
  [ -s "$REPORTS/ruff.sarif" ] || rm -f "$REPORTS/ruff.sarif"
else
  skip ruff "pip install ruff"
fi

if [ "$CHANGED" = 1 ] && [ ${#PY_TARGETS[@]} -eq 0 ]; then
  skip mypy "changed-mode: no changed Python files"
elif have mypy; then
  log "mypy"
  # Surgical CORRECTNESS flags (not annotation pedantry): --warn-unreachable
  # (dead code = a branch/condition bug), --strict-equality (== between
  # non-overlapping types is always False), --warn-no-return (a path falls
  # through to None). These surface logic bugs a type-checker can prove and
  # Semgrep can't; tag_map routes them to the `logic` axis.
  # --config-file pins OUR config so the scanned project's mypy config — and any
  # `plugins=` it declares, which mypy would import/execute — is never read.
  "$(bin mypy)" "${PY_TARGETS[@]}" --config-file="$ROOT/infra/mypy/waypoint.cfg" \
     --no-color-output --show-error-codes --show-column-numbers \
     --no-error-summary --ignore-missing-imports \
     --warn-unreachable --strict-equality --warn-no-return > "$REPORTS/_mypy.txt" 2>/dev/null || true
  "$PY" "$NORM/mypy_to_sarif.py" "$REPORTS/_mypy.txt" -o "$REPORTS/mypy.sarif"
else
  skip mypy "pip install mypy"
fi

if [ "$CHANGED" = 1 ]; then
  skip pip-audit "changed-mode: dependency scanner skipped (baseline covers it)"
elif have pip-audit; then
  while IFS= read -r req; do
    rel="$(relpath "$req" "$ROOT")"
    log "pip-audit ($rel)"
    "$(bin pip-audit)" -r "$req" -f json > "$REPORTS/_pipaudit.json" 2>/dev/null || true
    "$PY" "$NORM/pipaudit_to_sarif.py" "$REPORTS/_pipaudit.json" \
       -o "$REPORTS/pip-audit.sarif" --uri "$rel"
  done < <(find "$TARGET" -name requirements.txt -not -path '*/.venv/*' 2>/dev/null)
else
  skip pip-audit "pip install pip-audit"
fi

# --------------------------------------------------------------------------- #
# Rust: clippy (cargo JSON), cargo-audit, cargo-geiger
# --------------------------------------------------------------------------- #
if [ "$CHANGED" = 1 ]; then
  skip clippy "changed-mode: crate-level scanner skipped (baseline covers it)"
elif have cargo && rustup component list --installed 2>/dev/null | grep -q clippy; then
  while IFS= read -r manifest; do
    crate="$(dirname "$manifest")"; rel="$(relpath "$crate" "$ROOT")"
    log "clippy ($rel)"
    # Default clippy groups (correctness/suspicious/complexity/perf) PLUS a curated
    # set of `restriction` lints that surface real panic/hardening surface clippy
    # otherwise allows. We deliberately do NOT enable the pervasive ones
    # (arithmetic_side_effects, indexing_slicing) or pedantic/style — those would
    # flood the ranker with non-hardening noise; our Semgrep rules target the
    # surgical cases instead.
    ( cd "$crate" && cargo clippy --message-format=json --quiet 2>/dev/null -- \
        -W clippy::unwrap_used -W clippy::expect_used -W clippy::panic \
        -W clippy::unwrap_in_result -W clippy::mem_forget \
        -W clippy::todo -W clippy::unimplemented ) \
       > "$REPORTS/_clippy.jsonl" || true
    "$PY" "$NORM/clippy_to_sarif.py" "$REPORTS/_clippy.jsonl" \
       -o "$REPORTS/clippy.sarif" --base "$rel"
  done < <(find "$TARGET" -name Cargo.toml -not -path '*/target/*' 2>/dev/null)
else
  skip clippy "rustup component add clippy"
fi

if [ "$CHANGED" = 1 ]; then
  skip cargo-audit "changed-mode: crate-level scanner skipped (baseline covers it)"
elif have cargo-audit; then
  while IFS= read -r manifest; do
    crate="$(dirname "$manifest")"
    log "cargo-audit ($(relpath "$crate" "$ROOT"))"
    ( cd "$crate" && cargo audit --json 2>/dev/null ) > "$REPORTS/_cargoaudit.json" || true
    # cargo-audit JSON -> reuse osv-style? emit via a tiny inline pass omitted; keep raw for now
  done < <(find "$TARGET" -name Cargo.toml -not -path '*/target/*' 2>/dev/null)
else
  skip cargo-audit "cargo install cargo-audit"
fi

if [ "$CHANGED" = 1 ]; then
  skip cargo-geiger "changed-mode: crate-level scanner skipped (baseline covers it)"
elif have cargo-geiger; then
  while IFS= read -r manifest; do
    crate="$(dirname "$manifest")"; rel="$(relpath "$manifest" "$ROOT")"
    log "cargo-geiger ($rel)"
    ( cd "$crate" && cargo geiger --output-format Json 2>/dev/null ) > "$REPORTS/_geiger.json" || true
    "$PY" "$NORM/geiger_to_sarif.py" "$REPORTS/_geiger.json" -o "$REPORTS/cargo-geiger.sarif" --uri "$rel"
  done < <(find "$TARGET" -name Cargo.toml -not -path '*/target/*' 2>/dev/null)
else
  skip cargo-geiger "cargo install cargo-geiger"
fi

# --------------------------------------------------------------------------- #
# JS/TS: eslint (needs local install) ; osv-scanner (native SARIF)
# --------------------------------------------------------------------------- #
# ESLint runs WAYPOINT-OWNED only (never the target's binary/config/plugins — all of
# which are attacker-controlled code). --no-config-lookup + our flat config means a
# scanned project's eslint.config.* is never read or executed.
ESLW="$ROOT/node_modules/.bin/eslint"
ECFG="$ROOT/infra/eslint/waypoint.eslint.config.mjs"
if [ "$CHANGED" = 1 ] && [ ${#TS_TARGETS[@]} -eq 0 ]; then
  skip eslint "changed-mode: no changed JS/TS files"
elif [ -x "$ESLW" ]; then
  log "eslint (waypoint-owned, isolated config)"
  if [ "$CHANGED" = 1 ]; then
    "$ESLW" --no-config-lookup --config "$ECFG" -f @microsoft/eslint-formatter-sarif \
       -o "$REPORTS/eslint.sarif" "${TS_TARGETS[@]}" 2>/dev/null || true
  else
    "$ESLW" --no-config-lookup --config "$ECFG" -f @microsoft/eslint-formatter-sarif \
       -o "$REPORTS/eslint.sarif" "$TARGET" 2>/dev/null || true
  fi
  [ -s "$REPORTS/eslint.sarif" ] || rm -f "$REPORTS/eslint.sarif"
else
  skip eslint "install Waypoint's own ESLint (detectors/install.sh --eslint) — we never run the target's eslint (code-exec risk)"
fi

if [ "$CHANGED" = 1 ]; then
  skip osv-scanner "changed-mode: dependency scanner skipped (baseline covers it)"
elif have osv-scanner; then
  log "osv-scanner (native SARIF)"
  "$(bin osv-scanner)" --format sarif --recursive "$TARGET" > "$REPORTS/osv-scanner.sarif" 2>/dev/null || true
  [ -s "$REPORTS/osv-scanner.sarif" ] || rm -f "$REPORTS/osv-scanner.sarif"
else
  skip osv-scanner "brew install osv-scanner"
fi

# --------------------------------------------------------------------------- #
# Cross-cutting: gitleaks (native SARIF), trivy (native SARIF), codeql (gated)
# --------------------------------------------------------------------------- #
if [ "$CHANGED" = 1 ]; then
  skip gitleaks "changed-mode: repo-level scanner skipped (baseline covers it)"
elif have gitleaks; then
  log "gitleaks (native SARIF)"
  "$(bin gitleaks)" detect --no-git --source "$TARGET" \
     --report-format sarif --report-path "$REPORTS/gitleaks.sarif" 2>/dev/null || true
  [ -s "$REPORTS/gitleaks.sarif" ] || rm -f "$REPORTS/gitleaks.sarif"
else
  skip gitleaks "brew install gitleaks"
fi

# trufflehog (optional): VERIFIED secrets — it confirms the credential is live, so
# its findings are high-precision (a real upgrade over regex secret scanning). JSONL
# -> SARIF via our normalizer; the secret value is never written into a beacon.
if [ "$CHANGED" = 1 ]; then
  skip trufflehog "changed-mode: repo-level scanner skipped (baseline covers it)"
elif have trufflehog; then
  log "trufflehog (verified secrets → SARIF)"
  run_to 240 "$(bin trufflehog)" filesystem "$TARGET" --only-verified --json --no-update \
     > "$REPORTS/_trufflehog.jsonl" 2>/dev/null || true
  "$PY" "$NORM/trufflehog_to_sarif.py" "$REPORTS/_trufflehog.jsonl" -o "$REPORTS/trufflehog.sarif" 2>/dev/null || true
  [ -s "$REPORTS/trufflehog.sarif" ] || rm -f "$REPORTS/trufflehog.sarif"
else
  skip trufflehog "brew install trufflehog (verified-secret scanning; high precision)"
fi

if [ "$CHANGED" = 1 ]; then
  skip trivy "changed-mode: repo-level scanner skipped (baseline covers it)"
elif have trivy; then
  TRIVY="$(bin trivy)"
  # Pass 1 — IaC misconfig (Terraform/CloudFormation/Dockerfile/Kubernetes): the
  # "won't blow up on AWS" coverage (public S3, open security groups, IAM *,
  # unencrypted RDS, root containers, ...). Offline-safe via cached checks; run
  # as its own pass so it lands even when the vuln DB is unavailable.
  log "trivy: IaC misconfig (native SARIF)"
  run_to 180 "$TRIVY" fs --quiet --scanners misconfig --skip-check-update \
     --format sarif --output "$REPORTS/trivy-misconfig.sarif" "$TARGET" 2>/dev/null || true
  [ -s "$REPORTS/trivy-misconfig.sarif" ] || rm -f "$REPORTS/trivy-misconfig.sarif"
  # Pass 2 — dependency CVEs + secrets (best-effort; needs the vuln DB / network).
  log "trivy: dependency CVEs + secrets (native SARIF, best-effort)"
  run_to 240 "$TRIVY" fs --quiet --scanners vuln,secret \
     --format sarif --output "$REPORTS/trivy-vuln.sarif" "$TARGET" 2>/dev/null || true
  [ -s "$REPORTS/trivy-vuln.sarif" ] || rm -f "$REPORTS/trivy-vuln.sarif"
else
  skip trivy "brew install trivy"
fi

# CodeQL (cross-file taint) is its own OPT-IN lane now: detectors/run_codeql.sh,
# invoked by `bin/waypoint --codeql` / `--all`. A whole-program DB build is far
# too slow to run on every default scan, so it no longer runs inline here — the
# default `bin/waypoint <dir>` stays fast.

# --------------------------------------------------------------------------- #
log "done. per-tool SARIF in reports/:"
ls -1 "$REPORTS"/*.sarif 2>/dev/null | sed 's#.*/#    #' || log "  (none — install some detectors)"
log "next: $PY detectors/merge_sarif.py reports/*.sarif -o reports/beacons.sarif"
