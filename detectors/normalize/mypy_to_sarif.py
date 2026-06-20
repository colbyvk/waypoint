#!/usr/bin/env python3
"""
mypy_to_sarif.py — normalize mypy's default text output into SARIF.

mypy has no SARIF formatter. Run it with `--no-color-output --show-error-codes
--show-column-numbers` and pipe the text here. Lines look like:
    path/to/file.py:88:13: error: Item "None" has no attribute "x"  [union-attr]
Axes are applied by merge_sarif via tag_map's `mypy` block (union-attr ->
edge-case None-deref, etc.).

Usage: mypy_to_sarif.py mypy.txt -o mypy.sarif   (INPUT '-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

# file:line[:col]: level: message  [code]
_LINE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
    r"(?P<level>error|warning|note):\s*(?P<msg>.*?)(?:\s+\[(?P<code>[\w-]+)\])?\s*$"
)
_LEVEL = {"error": "error", "warning": "warning", "note": "note"}


def convert(lines) -> dict:
    sarif = S.empty_sarif("mypy")
    out = sarif["runs"][0]["results"]
    for line in lines:
        m = _LINE.match(line.rstrip("\n"))
        if not m:
            continue
        out.append(S.make_result(
            rule_id=m.group("code") or "mypy",
            level=_LEVEL.get(m.group("level"), "warning"),
            message=m.group("msg"),
            uri=m.group("file"),
            start_line=int(m.group("line")),
            start_col=int(m.group("col")) if m.group("col") else None,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    fh = sys.stdin if a.input == "-" else open(a.input, encoding="utf-8")
    sarif = convert(fh)
    S.write_sarif(sarif, a.out)
    print(f"mypy_to_sarif: {len(sarif['runs'][0]['results'])} diagnostics -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
