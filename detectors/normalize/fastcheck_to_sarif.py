#!/usr/bin/env python3
"""
fastcheck_to_sarif.py — fast-check (TS/JS) property-test failures -> Waypoint
SARIF (logic + edge-case).

fast-check is property-based testing for TypeScript/JavaScript (and therefore
React). On failure it prints `Property failed after N tests`, the shrunk
`Counterexample: [...]`, and the underlying error, with a stack trace. Each
failure becomes a `logic` beacon located at the deepest non-test source frame,
carrying the **counterexample** as the reproducing input.

Usage: fastcheck_to_sarif.py jest.out -o reports/fastcheck.sarif  ('-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_FAILED = re.compile(r"Property failed after \d+ test")
_COUNTER = re.compile(r"Counterexample:\s*(?P<v>.+)")
_GOTERR = re.compile(r"Got error:\s*(?P<v>.+)")
# A JS/TS stack frame: "at fn (path:line:col)" or "at path:line:col".
_JSLOC = re.compile(r"([\w./\\@-]+\.(?:tsx?|jsx?|mjs|cjs)):(\d+):\d+")
_SKIP_FRAME = ("node_modules", "internal/", "node:internal")


def _is_test_frame(path: str) -> bool:
    return bool(re.search(r"(\.test\.|\.spec\.|/tests?/|__tests__)", path))


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _blame_location(block: str):
    locs = [(m.group(1), int(m.group(2))) for m in _JSLOC.finditer(block)]
    locs = [(p, n) for (p, n) in locs if not any(s in p for s in _SKIP_FRAME)]
    if not locs:
        return None
    real = [(p, n) for (p, n) in locs if not _is_test_frame(p)]
    return (real or locs)[0]   # first (shallowest) user frame is the property body


def _blocks(text: str):
    idxs = [m.start() for m in _FAILED.finditer(text)]
    if not idxs:
        return []
    bounds = idxs + [len(text)]
    # include a little preceding context so the test-name line is in the block
    return [text[max(0, bounds[i] - 200):bounds[i + 1]] for i in range(len(idxs))]


def convert(text: str) -> dict:
    sarif = S.empty_sarif("fast-check")
    out = sarif["runs"][0]["results"]
    for block in _blocks(text):
        cm = _COUNTER.search(block)
        if not cm:
            continue
        loc = _blame_location(block)
        if not loc:
            continue
        path, line = loc
        repro = _collapse(cm.group("v"))
        em = _GOTERR.search(block)
        prop = _collapse(em.group("v")) if em else "a property/invariant did not hold"
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
            rule_id="fast-check/falsified-property",
            level="error",
            message=f"Property failed — counterexample: {repro}",
            uri=path,
            start_line=line,
            properties=props,
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="fast-check (jest/vitest/node) output ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif = convert(text)
    S.write_sarif(sarif, a.out)
    print(f"fastcheck_to_sarif: {len(sarif['runs'][0]['results'])} falsified propert(ies) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
