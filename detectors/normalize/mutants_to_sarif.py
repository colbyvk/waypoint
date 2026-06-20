#!/usr/bin/env python3
"""
mutants_to_sarif.py — cargo-mutants outcomes.json -> Waypoint SARIF (logic axis).

A SURVIVING mutant (MissedMutant / Timeout) is a place where cargo-mutants changed
your logic and the test suite still passed — i.e. that branch is either untested
or its behavior doesn't matter (often: a real correctness gap). Each becomes a
`logic` beacon so the agent can decide whether it's a missing test or a real bug.

Usage: mutants_to_sarif.py mutants.out/outcomes.json -o reports/mutants.sarif
"""
from __future__ import annotations
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

# Outcomes whose mutant survived the suite (a test gap / possible logic bug).
SURVIVED = {"MissedMutant", "Timeout", "missed", "timeout"}


def _summary_name(summary) -> str:
    if isinstance(summary, str):
        return summary
    if isinstance(summary, dict):
        return next(iter(summary), "")
    return ""


def convert(data: dict) -> dict:
    sarif = S.empty_sarif("cargo-mutants")
    out = sarif["runs"][0]["results"]
    for o in (data.get("outcomes") or []):
        if _summary_name(o.get("summary")) not in SURVIVED:
            continue
        scen = o.get("scenario") or {}
        mut = scen.get("Mutant") or scen.get("mutant") or {}
        if not isinstance(mut, dict):
            continue
        span = mut.get("span") or {}
        line = (span.get("start") or {}).get("line") or mut.get("line") or 1
        fn = mut.get("function")
        fn = fn.get("function_name") if isinstance(fn, dict) else (fn or "function")
        repl = mut.get("replacement") or mut.get("genre") or "mutation"
        out.append(S.make_result(
            rule_id="cargo-mutants/surviving-mutant",
            level="warning",
            message=f"Surviving mutant in {fn}: `{repl}` was not caught by the test suite.",
            uri=mut.get("file") or "?",
            start_line=int(line),
            properties={
                "waypoint_axes": ["logic"],
                "waypoint_hypothesis": "this code can be mutated without any test failing — is the branch untested, or is the logic actually wrong?",
            },
        ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="cargo-mutants outcomes.json ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    raw = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    data = json.loads(raw) if raw.strip() else {}
    sarif = convert(data)
    S.write_sarif(sarif, a.out)
    print(f"mutants_to_sarif: {len(sarif['runs'][0]['results'])} surviving mutants -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
