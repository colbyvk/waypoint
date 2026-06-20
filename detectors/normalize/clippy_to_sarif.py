#!/usr/bin/env python3
"""
clippy_to_sarif.py — normalize `cargo clippy --message-format=json` into SARIF.

Clippy emits the rustc JSON diagnostic stream (newline-delimited objects), not
SARIF. We keep `compiler-message` entries that carry a lint code (clippy:: or a
rustc lint) at warning/error level, using each diagnostic's primary span for
the location. Axes are applied by merge_sarif via tag_map's `clippy` block
(*unwrap*/*panic* -> edge-case, *await_holding_lock* -> concurrency, ...).

This replaces the `clippy-sarif` crate from the spec with a zero-install Python
wrapper, so the team needs no extra Rust tooling to get SARIF.

Usage: clippy_to_sarif.py clippy.jsonl -o clippy.sarif [--base rust_service]
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_LEVEL = {"error": "error", "warning": "warning", "note": "note", "help": "note"}


def convert(lines, base_prefix: str) -> dict:
    sarif = S.empty_sarif("clippy")
    out = sarif["runs"][0]["results"]
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if obj.get("reason") != "compiler-message":
            continue
        msg = obj.get("message") or {}
        code = (msg.get("code") or {}).get("code")
        level = _LEVEL.get(msg.get("level", ""), None)
        if not code or level is None:
            continue  # skip uncoded notes and rendered-only entries
        spans = [s for s in msg.get("spans", []) if s.get("is_primary")] or msg.get("spans", [])
        if not spans:
            continue
        sp = spans[0]
        uri = sp.get("file_name", "")
        if base_prefix and uri and not uri.startswith(base_prefix):
            uri = os.path.join(base_prefix, uri)
        out.append(S.make_result(
            rule_id=code,
            level=level,
            message=msg.get("message", code),
            uri=uri,
            start_line=sp.get("line_start", 1),
            end_line=sp.get("line_end"),
            start_col=sp.get("column_start"),
            end_col=sp.get("column_end"),
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="cargo clippy --message-format=json output ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--base", default="", help="path prefix to prepend to crate-relative file names")
    a = ap.parse_args(argv)
    fh = sys.stdin if a.input == "-" else open(a.input, encoding="utf-8")
    sarif = convert(fh, a.base)
    S.write_sarif(sarif, a.out)
    print(f"clippy_to_sarif: {len(sarif['runs'][0]['results'])} diagnostics -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
