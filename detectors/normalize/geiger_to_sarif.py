#!/usr/bin/env python3
"""
geiger_to_sarif.py — normalize `cargo geiger --output-format Json` into SARIF.

cargo-geiger counts `unsafe` usage per crate. There is no per-line location, so
each package whose used-unsafe count is > 0 becomes one beacon pointed at the
crate manifest — a direct concurrency/memory signal (spec §6.2). Axes come from
tag_map's `cargo-geiger` block (-> concurrency, security).

geiger's JSON schema has drifted across versions; this reader is intentionally
tolerant and best-effort. If geiger is not installed, run_all.sh skips it.

Usage: geiger_to_sarif.py geiger.json -o geiger.sarif [--uri rust_service/Cargo.toml]
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402


def _used_unsafe(counts: dict) -> int:
    """Sum the 'used' unsafe counters across functions/exprs/impls/traits."""
    total = 0
    for k in ("functions", "exprs", "item_impls", "item_traits", "methods"):
        block = counts.get(k) or {}
        if isinstance(block, dict):
            total += int(block.get("used", 0) or 0)
    return total


def convert(data: dict, default_uri: str) -> dict:
    sarif = S.empty_sarif("cargo-geiger")
    out = sarif["runs"][0]["results"]
    for pkg in data.get("packages", []) or []:
        info = pkg.get("package", pkg)
        pid = (info.get("id") or info) if isinstance(info, dict) else info
        name = pid.get("name", "crate") if isinstance(pid, dict) else str(pid)
        unsafety = pkg.get("unsafety", {}) or {}
        used = _used_unsafe(unsafety.get("used", {}) or {})
        if used <= 0:
            continue
        out.append(S.make_result(
            rule_id="cargo-geiger/unsafe-used",
            level="warning" if used > 5 else "note",
            message=f"{name}: {used} used `unsafe` expressions/items (cargo-geiger).",
            uri=default_uri,
            start_line=None,   # crate-level signal, not a specific line
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--uri", default="Cargo.toml")
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except ValueError:
        data = {}
    sarif = convert(data, a.uri)
    S.write_sarif(sarif, a.out)
    print(f"geiger_to_sarif: {len(sarif['runs'][0]['results'])} unsafe crates -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
