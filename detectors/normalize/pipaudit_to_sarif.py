#!/usr/bin/env python3
"""
pipaudit_to_sarif.py — normalize `pip-audit -f json` into SARIF.

pip-audit emits columns/json/cyclonedx/markdown, not SARIF. Each dependency
vulnerability becomes one beacon located at the dependency manifest (pass --uri
to point at the right requirements file). Axes are applied by merge_sarif via
tag_map's `pip-audit` block (all dependency CVEs -> security).

Usage: pipaudit_to_sarif.py pip-audit.json -o out.sarif --uri requirements.txt
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402


def convert(data, uri: str) -> dict:
    sarif = S.empty_sarif("pip-audit")
    out = sarif["runs"][0]["results"]
    # pip-audit JSON is either {"dependencies": [...]} or a bare list (older).
    deps = data.get("dependencies", data) if isinstance(data, dict) else data
    for dep in deps or []:
        name, version = dep.get("name", "?"), dep.get("version", "?")
        for v in dep.get("vulns", []) or []:
            fix = ", ".join(v.get("fix_versions", []) or []) or "no fix listed"
            desc = (v.get("description", "") or "").strip().replace("\n", " ")
            out.append(S.make_result(
                rule_id=v.get("id", "VULN"),
                level="warning",
                message=f"{name} {version}: {v.get('id', '')} — {desc[:200]} (fix: {fix})",
                uri=uri,
                start_line=None,   # dependency CVE: identified by advisory, not line
            ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--uri", default="requirements.txt", help="path to the dependency manifest")
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    data = json.loads(raw) if raw.strip() else {"dependencies": []}
    sarif = convert(data, a.uri)
    S.write_sarif(sarif, a.out)
    print(f"pipaudit_to_sarif: {len(sarif['runs'][0]['results'])} vulns -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
