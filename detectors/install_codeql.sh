#!/usr/bin/env bash
# ============================================================================
# install_codeql.sh — one-command, INTEGRITY-VERIFIED CodeQL install.
#
# Downloads a PINNED CodeQL bundle (CLI + standard query packs), verifies it
# (fail-closed), and prints the PATH line. After this, `bin/waypoint <dir>
# --codeql` / `--all` runs cross-file taint live.
#
# Verification precedence (any one passing = OK; none = REFUSE to install):
#   1. WAYPOINT_CODEQL_SHA256 env override   2. pinned SHA-256 below
#   3. `gh attestation verify` (if gh present)
#
#   usage: detectors/install_codeql.sh [INSTALL_DIR]   (default: <waypoint>/.codeql)
# ============================================================================
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-$ROOT/.codeql}"

# --- Pinned release + expected SHA-256 per platform (bump together) ---------
CODEQL_VERSION="codeql-bundle-v2.25.6"
SHA256_osx64="29ffd26c5a3a455625dde92886a92514812987d0f70c46fd457db96516f2243b"
SHA256_linux64=""   # not pinned here — falls back to gh attestation / env override

if command -v codeql >/dev/null 2>&1; then
  echo "codeql already on PATH: $(command -v codeql)"
  codeql version 2>/dev/null | head -1 || true
  exit 0
fi

case "$(uname -s)" in
  Darwin) asset="codeql-bundle-osx64.tar.gz";   expected="$SHA256_osx64" ;;
  Linux)  asset="codeql-bundle-linux64.tar.gz"; expected="$SHA256_linux64" ;;
  *) echo "Unsupported OS '$(uname -s)'. Install manually from" \
          "https://github.com/github/codeql-action/releases" >&2; exit 1 ;;
esac
url="https://github.com/github/codeql-action/releases/download/$CODEQL_VERSION/$asset"

mkdir -p "$DEST"; tgz="$DEST/$asset"
echo "Downloading $CODEQL_VERSION ($asset) → $DEST/  (~1.3 GB; one-time) …"
if command -v curl >/dev/null 2>&1; then curl -fL --retry 3 "$url" -o "$tgz"
elif command -v wget >/dev/null 2>&1; then wget -O "$tgz" "$url"
else echo "need curl or wget on PATH" >&2; exit 1; fi

# --- verify integrity, FAIL CLOSED -----------------------------------------
verify_sha() {  # $1 = expected hex
  local got; got="$(shasum -a 256 "$tgz" | cut -d' ' -f1)"
  if [ "$got" = "$1" ]; then echo "  SHA-256 OK"; return 0; fi
  echo "  SHA-256 MISMATCH: got $got, wanted $1" >&2; return 1
}
verified=0
if [ -n "${WAYPOINT_CODEQL_SHA256:-}" ]; then
  echo "verifying against WAYPOINT_CODEQL_SHA256 …"; verify_sha "$WAYPOINT_CODEQL_SHA256" && verified=1 || true
elif [ -n "$expected" ]; then
  echo "verifying against pinned SHA-256 …"; verify_sha "$expected" && verified=1 || true
elif command -v gh >/dev/null 2>&1; then
  echo "verifying via GitHub attestation (gh) …"
  if gh attestation verify "$tgz" --repo github/codeql-action >/dev/null 2>&1; then
    echo "  attestation OK"; verified=1
  else echo "  attestation unavailable/failed" >&2; fi
fi
if [ "$verified" != 1 ]; then
  rm -f "$tgz"
  echo "REFUSING to install an unverified CodeQL bundle." >&2
  echo "Pin its SHA-256 in this script, set WAYPOINT_CODEQL_SHA256=<sha>, or install gh." >&2
  exit 1
fi

echo "Extracting …"
tar -xzf "$tgz" --no-same-owner -C "$DEST"
rm -f "$tgz"
CQ="$DEST/codeql/codeql"; [ -x "$CQ" ] || { echo "extract failed: $CQ not found" >&2; exit 1; }

echo
echo "[ok] CodeQL installed + verified. Add it to PATH (and your shell profile):"
echo "    export PATH=\"$DEST/codeql:\$PATH\""
echo
echo "Then verify:   codeql version"
echo "And run:       bin/waypoint <dir> --codeql      (cross-file taint)"
