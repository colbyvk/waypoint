#!/usr/bin/env bash
# ============================================================================
# examples/demo.sh — a ~20-second taste of Waypoint on the bundled, intentionally
# vulnerable sample monorepo. Shows the capability banner, the ranked BEACONS
# (what it found), and the DARK ZONE (what it could NOT verify). Fast tier only —
# $0, no target code executed, safe to run anywhere.
#
# Want a recording for your README? Wrap this in asciinema:
#     asciinema rec -c 'examples/demo.sh' demo.cast
#     # then: svg-term --in demo.cast --out docs/demo.svg   (or upload the cast)
# ============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[ -x .venv/bin/python ] || { echo "Run detectors/install.sh first (one time)."; exit 1; }

bin/wipe-beacons >/dev/null 2>&1 || true
printf '\n$ bin/waypoint samples/monorepo\n\n'
bin/waypoint samples/monorepo

printf '\n──────── BEACONS — what it found (top of beacons/INDEX.md) ────────\n'
grep -E '^\| \[' beacons/INDEX.md | head -6

printf '\n──────── DARK ZONE — what it could NOT verify (beacons/BLINDSPOTS.md) ────────\n'
grep -E '^\| [0-9]' beacons/BLINDSPOTS.md | head -5

printf '\nFull set: reports/ranked.sarif · this is the fast tier ($0). Add --deep / --investigate for more.\n'
