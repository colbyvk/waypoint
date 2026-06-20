#!/usr/bin/env python3
"""
semgrep_to_sarif.py — normalize `semgrep --json` into Waypoint SARIF.

Why this wrapper exists even though Semgrep can emit SARIF directly: Semgrep's
SARIF exporter DROPS custom rule metadata (we verified waypoint_axes /
waypoint_hypothesis never reach rule.properties). Its JSON output keeps them
under result.extra.metadata. So we read JSON and re-emit SARIF with our axes
and hypothesis preserved on result.properties, plus a cleaned rule id
(Semgrep path-prefixes ids like `rules.semgrep.concurrency.waypoint-...`).

For community rules that carry no waypoint_axes, we infer an axis from
Semgrep's own category/cwe/owasp metadata so those beacons are tagged too.

Usage: semgrep_to_sarif.py semgrep.json -o semgrep.sarif   (INPUT '-' = stdin)
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_LEVEL = {"ERROR": "error", "WARNING": "warning", "INFO": "note",
          "HIGH": "error", "MEDIUM": "warning", "LOW": "note",
          "high": "error", "medium": "warning", "low": "note", "info": "note"}


def clean_id(check_id: str) -> str:
    return check_id[check_id.index("waypoint-"):] if "waypoint-" in check_id else check_id


def infer_axes(meta: dict) -> list[str]:
    cat = (meta.get("category") or "").lower()
    blob = " ".join(str(x).lower() for x in (
        (meta.get("cwe") or []) + (meta.get("owasp") or []) + (meta.get("tags") or [])
    ))
    text = cat + " " + blob
    axes = set()
    if cat == "security" or any(k in text for k in
            ("cwe", "owasp", "injection", "xss", "ssrf", "traversal", "secret", "crypto", "auth")):
        axes.add("security")
    if any(k in text for k in ("race", "concurren", "async", "thread", "lock", "atomic")):
        axes.add("concurrency")
    if any(k in text for k in ("dos", "redos", "resource", "complexity", "amplif")):
        axes.add("abuse")
    if cat in ("correctness", "best-practice", "maintainability", "performance") or not axes:
        axes.add("edge-case")
    return sorted(axes)


def convert(data: dict) -> dict:
    sarif = S.empty_sarif("semgrep")
    out = sarif["runs"][0]["results"]
    for r in data.get("results", []):
        extra = r.get("extra", {})
        meta = extra.get("metadata", {}) or {}
        rid = clean_id(r.get("check_id", "semgrep-unknown"))
        level = _LEVEL.get(str(extra.get("severity", "WARNING")), "warning")
        props: dict = {}
        axes = meta.get("waypoint_axes") or infer_axes(meta)
        props["waypoint_axes"] = axes
        if meta.get("waypoint_hypothesis"):
            props["waypoint_hypothesis"] = meta["waypoint_hypothesis"]
        if meta.get("waypoint_subtags"):
            props["waypoint_subtags"] = meta["waypoint_subtags"]
        if meta.get("waypoint_severity_prior") is not None:
            props["waypoint_severity_prior"] = meta["waypoint_severity_prior"]
        out.append(S.make_result(
            rule_id=rid, level=level,
            message=extra.get("message", "") or rid,
            uri=r.get("path", ""),
            start_line=(r.get("start") or {}).get("line", 1),
            end_line=(r.get("end") or {}).get("line"),
            start_col=(r.get("start") or {}).get("col"),
            end_col=(r.get("end") or {}).get("col"),
            properties=props,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="semgrep --json output ('-' for stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    data = json.loads(raw) if raw.strip() else {"results": []}
    S.write_sarif(convert(data), a.out)
    print(f"semgrep_to_sarif: {len(data.get('results', []))} findings -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
