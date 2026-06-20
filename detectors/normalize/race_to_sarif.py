#!/usr/bin/env python3
"""
race_to_sarif.py — race-detector output -> Waypoint SARIF (logic + concurrency).

Ingests Go `-race` and ThreadSanitizer (C/C++/Rust `-Zsanitizer=thread`) reports.
Each "DATA RACE" block becomes one beacon located at the first source line in the
block. A race detector reports REAL runtime races (not smells) — high-confidence
logic beacons; the agent confirms the unsynchronized access and the fix.

Usage: race_to_sarif.py race.txt -o reports/race.sarif   ('-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_HDR = re.compile(r"(WARNING:\s*DATA RACE|ThreadSanitizer:\s*data race|WARNING:\s*ThreadSanitizer)")
_SRC = re.compile(r"([\w./\\-]+\.(?:rs|go|c|cc|cpp|cxx|h|hpp)):(\d+)")


def convert(text: str) -> dict:
    sarif = S.empty_sarif("race-detector")
    out = sarif["runs"][0]["results"]
    blocks, cur = [], None
    for ln in text.splitlines():
        if _HDR.search(ln):
            if cur is not None:
                blocks.append(cur)
            cur = [ln]
        elif cur is not None:
            cur.append(ln)
    if cur is not None:
        blocks.append(cur)

    for block in blocks:
        loc = next((m for ln in block for m in [_SRC.search(ln)] if m), None)
        if not loc:
            continue
        out.append(S.make_result(
            rule_id="race-detector/data-race",
            level="error",
            message="Data race detected at runtime (concurrent unsynchronized access).",
            uri=loc.group(1),
            start_line=int(loc.group(2)),
            properties={
                "waypoint_axes": ["logic", "concurrency"],
                "waypoint_hypothesis": "a data race was observed here at runtime — confirm the unsynchronized shared access and the interleaving that triggers it",
            },
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="race detector text output ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif = convert(text)
    S.write_sarif(sarif, a.out)
    print(f"race_to_sarif: {len(sarif['runs'][0]['results'])} data races -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
