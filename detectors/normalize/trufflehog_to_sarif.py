#!/usr/bin/env python3
"""
trufflehog_to_sarif.py — normalize `trufflehog filesystem --json` (JSONL) into SARIF.

trufflehog emits one JSON object per line. Run with --only-verified and each finding
is a VERIFIED live secret (the detector confirmed the credential actually works) —
much higher precision than a regex secret scanner. We NEVER write the secret value
(`Raw`) into the beacon.

Usage: trufflehog_to_sarif.py tf.jsonl -o trufflehog.sarif   (INPUT '-' = stdin)
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402


def _loc(obj: dict):
    data = ((obj.get("SourceMetadata") or {}).get("Data") or {})
    src = data.get("Filesystem") or data.get("Directory") or data.get("Git") or {}
    return (src.get("file") or src.get("path") or ""), int(src.get("line") or 1)


def convert(lines) -> tuple[dict, int]:
    sarif = S.empty_sarif("trufflehog")
    out = sarif["runs"][0]["results"]
    n = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(obj, dict) or "DetectorName" not in obj:
            continue
        verified = bool(obj.get("Verified"))
        det = obj.get("DetectorName", "secret")
        uri, line = _loc(obj)
        out.append(S.make_result(
            rule_id=f"trufflehog-{det}",
            level="error" if verified else "warning",
            message=(f"{'VERIFIED live' if verified else 'unverified'} secret: {det} "
                     "(value redacted — rotate the credential)"),
            uri=uri, start_line=line,
            properties={
                "waypoint_axes": ["abuse", "security"],
                "waypoint_severity_prior": 0.95 if verified else 0.6,
                "waypoint_hypothesis": (
                    f"a {'verified, live ' if verified else ''}{det} secret is committed "
                    "in source — confirm and ROTATE it (assume compromised)."),
            },
        ))
        n += 1
    return sarif, n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif, n = convert(raw.splitlines())
    S.write_sarif(sarif, a.out)
    print(f"trufflehog_to_sarif: {n} secret finding(s) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
