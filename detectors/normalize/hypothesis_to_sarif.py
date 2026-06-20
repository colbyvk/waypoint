#!/usr/bin/env python3
"""
hypothesis_to_sarif.py — Hypothesis property-test failures -> Waypoint SARIF
(logic + edge-case).

Property-based testing asserts an INVARIANT ("for all inputs, lo <= clamp(x) <=
hi") and lets Hypothesis search for a counterexample, then SHRINK it to the
minimal failing input. A falsifying example is high-signal evidence of a logic
bug that needs no spec and no hand-written tests — so each becomes a `logic`
beacon carrying the **minimal reproducing input** and the **property** it broke.

We parse pytest+Hypothesis console output: each FAILURES section gives one
beacon, located at the deepest non-test source frame, with the "Falsifying
example:" call captured as the reproducing input.

Usage: hypothesis_to_sarif.py pytest.out -o reports/hypothesis.sarif  ('-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

# A pytest FAILURES section header: "____ test_name ____".
_SECTION = re.compile(r"^_{3,}\s*(.+?)\s*_{3,}\s*$", re.M)
# A python source frame "path/file.py:NN" (pytest tracebacks) — line REQUIRED.
_PYLOC = re.compile(r"([\w./\\-]+\.py):(\d+)")
# The shrunk counterexample Hypothesis prints. Capture from the call name
# through its closing paren, stopping before a blank line or a pytest rule so
# the summary lines never leak into the reproducing input.
_FALSIFY = re.compile(r"Falsifying example:\s*(?P<call>.+?\))\s*(?:\n[=_]{3,}|\n[ \t]*\n|\Z)", re.S)
# The assertion / error line pytest shows ("E   assert ...", "E   ValueError: ..").
_ASSERT = re.compile(r"^E\s+(.*\S)", re.M)
# Frames we never want to BLAME (the harness, the framework, stdlib).
_SKIP_FRAME = ("site-packages", "_pytest", "/hypothesis/", "hypothesis/",
               "conftest.py", "<stdin>")


def _is_test_frame(path: str) -> bool:
    bn = os.path.basename(path)
    return bn.startswith("test_") or bn.endswith("_test.py") or "/tests/" in path


def _blame_location(block: str):
    """Pick the source frame to put the beacon on: prefer the deepest (last)
    non-test, non-framework frame; fall back to the last test frame; else None."""
    locs = [(m.group(1), int(m.group(2))) for m in _PYLOC.finditer(block)]
    locs = [(p, n) for (p, n) in locs if not any(s in p for s in _SKIP_FRAME)]
    if not locs:
        return None
    real = [(p, n) for (p, n) in locs if not _is_test_frame(p)]
    return (real or locs)[-1]


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def convert(text: str) -> dict:
    sarif = S.empty_sarif("hypothesis")
    out = sarif["runs"][0]["results"]

    # Split into per-failure blocks on the pytest section rules; if there are no
    # section headers, treat the whole log as one block.
    starts = [m.start() for m in _SECTION.finditer(text)]
    blocks = []
    if starts:
        bounds = starts + [len(text)]
        for i in range(len(starts)):
            blocks.append(text[bounds[i]:bounds[i + 1]])
    else:
        blocks = [text]

    for block in blocks:
        fm = _FALSIFY.search(block)
        if not fm:
            continue  # a section without a falsifying example isn't a property failure
        loc = _blame_location(block)
        if not loc:
            continue
        path, line = loc
        repro = _collapse(fm.group("call"))
        am = _ASSERT.search(block)
        prop = _collapse(am.group(1)) if am else "a property/invariant did not hold"
        props = {
            "waypoint_axes": ["logic", "edge-case"],
            "waypoint_hypothesis": "a property-based test found an input that violates an invariant here — confirm the code is wrong (not the property)",
            "waypoint_property": prop,
            "waypoint_reproducing_input": repro,
        }
        subtags = S.property_relation_subtags(block)
        if subtags:
            props["waypoint_subtags"] = subtags
        out.append(S.make_result(
            rule_id="hypothesis/falsified-property",
            level="error",
            message=f"Property failed — Hypothesis shrank it to: {repro}",
            uri=path,
            start_line=line,
            properties=props,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="pytest+Hypothesis output ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif = convert(text)
    S.write_sarif(sarif, a.out)
    print(f"hypothesis_to_sarif: {len(sarif['runs'][0]['results'])} falsified propert(ies) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
