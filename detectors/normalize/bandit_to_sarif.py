#!/usr/bin/env python3
"""
bandit_to_sarif.py — normalize `bandit -f json` into SARIF.

The installed Bandit (1.9.x) has no SARIF formatter (formats are
csv/custom/html/json/screen/txt/xml/yaml), so we convert its JSON. The beacon's
axes/hypothesis are applied later by merge_sarif via tag_map.yaml's `bandit`
block, keyed on the Bandit test id (B602, B608, ...).

Usage: bandit_to_sarif.py bandit.json -o bandit.sarif   (INPUT '-' = stdin)
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_LEVEL = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}


def convert(data: dict) -> dict:
    sarif = S.empty_sarif("bandit")
    out = sarif["runs"][0]["results"]
    for r in data.get("results", []):
        rng = r.get("line_range") or [r.get("line_number", 1)]
        props = {}
        cwe = (r.get("issue_cwe") or {}).get("id")
        if cwe:
            props["cwe"] = f"CWE-{cwe}"
        out.append(S.make_result(
            rule_id=r.get("test_id", "bandit"),
            level=_LEVEL.get(str(r.get("issue_severity", "MEDIUM")).upper(), "warning"),
            message=f"{r.get('test_name', '')}: {r.get('issue_text', '')}".strip(": "),
            uri=r.get("filename", ""),
            start_line=r.get("line_number", 1),
            end_line=max(rng) if rng else r.get("line_number", 1),
            start_col=r.get("col_offset"),
            properties=props or None,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    data = json.loads(raw) if raw.strip() else {"results": []}
    S.write_sarif(convert(data), a.out)
    print(f"bandit_to_sarif: {len(data.get('results', []))} findings -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
