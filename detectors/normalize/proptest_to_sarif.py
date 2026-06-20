#!/usr/bin/env python3
"""
proptest_to_sarif.py — Rust proptest / quickcheck failures -> Waypoint SARIF
(logic + edge-case).

Rust's property testing (`proptest!` / `quickcheck`) searches for an input that
breaks an invariant and shrinks it to the minimal failing case. proptest panics
with `... ; minimal failing input: x = ...` at the assertion's source location;
quickcheck prints `[quickcheck] TEST FAILED. Arguments: (...)`. Each failure
becomes a `logic` beacon carrying the **minimal reproducing input**.

Usage: proptest_to_sarif.py cargo-test.out -o reports/proptest.sarif  ('-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

# A Rust panic begins a failure block. Both panic formats are supported:
#   new:  thread '..' panicked at src/x.rs:23:9:
#   old:  thread '..' panicked at 'msg', src/x.rs:23:9
_PANIC = re.compile(r"thread '.*?' panicked at ")
_RSLOC = re.compile(r"([\w./\\-]+\.rs):(\d+)(?::\d+)?")
_MINIMAL = re.compile(r"minimal failing input:\s*(?P<v>.+)")
_QCARGS = re.compile(r"\[quickcheck\][^\n]*?Arguments:\s*(?P<v>.+)", re.I)
_TESTFAIL = re.compile(r"(Test failed:[^\n]*?)(?:;\s*minimal failing input:|\n|$)")


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).rstrip(",")


def _blocks(text: str):
    """Split the log into one block per panic (a proptest/quickcheck failure)."""
    idxs = [m.start() for m in _PANIC.finditer(text)]
    if not idxs:
        # quickcheck without a Rust panic line — treat the whole log as one block
        return [text] if _QCARGS.search(text) else []
    bounds = idxs + [len(text)]
    return [text[bounds[i]:bounds[i + 1]] for i in range(len(idxs))]


def convert(text: str) -> dict:
    sarif = S.empty_sarif("proptest")
    out = sarif["runs"][0]["results"]
    for block in _blocks(text):
        loc = _RSLOC.search(block)
        if not loc:
            continue
        mm = _MINIMAL.search(block) or _QCARGS.search(block)
        if not mm:
            continue  # a panic with no shrunk input isn't a property counterexample
        repro = _collapse(mm.group("v"))
        tf = _TESTFAIL.search(block)
        prop = _collapse(tf.group(1)) if tf else "a property/invariant did not hold"
        props = {
            "waypoint_axes": ["logic", "edge-case"],
            "waypoint_hypothesis": "a property test found an input that violates an invariant here — confirm the code is wrong (not the property)",
            "waypoint_property": prop,
            "waypoint_reproducing_input": repro,
        }
        subtags = S.property_relation_subtags(block)
        if subtags:
            props["waypoint_subtags"] = subtags
        out.append(S.make_result(
            rule_id="proptest/falsified-property",
            level="error",
            message=f"Property failed — shrunk to minimal input: {repro}",
            uri=loc.group(1),
            start_line=int(loc.group(2)),
            properties=props,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="cargo test (proptest/quickcheck) output ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif = convert(text)
    S.write_sarif(sarif, a.out)
    print(f"proptest_to_sarif: {len(sarif['runs'][0]['results'])} falsified propert(ies) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
