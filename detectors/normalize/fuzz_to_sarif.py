#!/usr/bin/env python3
"""
fuzz_to_sarif.py — fuzzer crash output -> Waypoint SARIF (logic + edge-case).

A fuzzer feeds generated inputs until the code crashes (panic, deadly signal,
ASan abort, uncaught exception). A crash means a *reachable* input drives the
code into a crash/UB path — a logic/edge-case bug with a concrete trigger. This
wrapper understands the four-language fuzzers Waypoint wires up:

  * cargo-fuzz / libFuzzer (Rust, C/C++)  — Rust panic + native frames
  * Atheris (Python)                      — `Uncaught Python exception` + traceback
  * Jazzer.js (TypeScript/JavaScript)     — uncaught error + JS stack

Each crash becomes one beacon at the crash site, carrying the **reproducing
input** (the libFuzzer Base64 dump, or the saved crash-artifact path) so the
agent — or a human — can replay it.

Usage: fuzz_to_sarif.py crash.txt -o reports/fuzz.sarif   ('-' = stdin)
"""
from __future__ import annotations
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sariflib as S  # noqa: E402

_CRASH = re.compile(r"(ERROR: libFuzzer|deadly signal|panicked at|AddressSanitizer|"
                    r"ERROR: AddressSanitizer|SUMMARY: |Uncaught (?:Python )?[Ee]xception|"
                    r"Jazzer|== ?Java Exception)")

# Rust / C panic (cargo-fuzz, libFuzzer).
_PANIC = re.compile(r"panicked at:?\s*'?(?P<msg>[^'\n]+?)'?,?\s+(?P<file>[\w./\\-]+\.\w+):(?P<line>\d+)")
_FRAME = re.compile(r"\bin\s+\S+\s+([\w./\\-]+\.(?:rs|c|cc|cpp|cxx|go)):(\d+)")
_SRC = re.compile(r"([\w./\\-]+\.(?:rs|c|cc|cpp|cxx|go)):(\d+)")

# Python (Atheris) traceback frames + the exception line.
_PYFRAME = re.compile(r'File "(?P<file>[^"]+\.py)", line (?P<line>\d+)(?:, in (?P<fn>\S+))?')
_PYEXC = re.compile(r"^(?P<exc>[A-Za-z_][\w.]*(?:Error|Exception|Warning)):\s*(?P<m>.*)$", re.M)

# JS/TS (Jazzer.js) stack frames + the error line.
_JSFRAME = re.compile(r"at\s+(?:\S+\s+\()?(?P<file>[\w./\\@-]+\.(?:tsx?|jsx?|mjs|cjs)):(?P<line>\d+):\d+")
_JSERR = re.compile(r"(?:Uncaught (?:Exception|Error)|Got error|Error):\s*(?P<m>.+)", re.I)

# Reproducing input: libFuzzer base64 dump, or the saved crash-artifact path.
_B64 = re.compile(r"Base64:\s*(?P<v>\S+)")
_ARTIFACT = re.compile(r"Test unit written to\s+(?P<v>\S+)")

_PY_HARNESS = ("_fuzz.py", "atheris")
_JS_SKIP = ("node_modules", "internal/", "node:")


def _reproducing_input(text: str):
    bm = _B64.search(text)
    if bm:
        return "base64:" + bm.group("v")
    am = _ARTIFACT.search(text)
    if am:
        return "crash artifact: " + am.group("v")
    return None


def convert(text: str) -> dict:
    sarif = S.empty_sarif("fuzz")
    out = sarif["runs"][0]["results"]
    if not _CRASH.search(text):
        return sarif  # no crash in this output

    msg, file, line = None, None, None

    # 1) Rust / C panic (cargo-fuzz, libFuzzer).
    pm = _PANIC.search(text)
    if pm:
        msg, file, line = pm.group("msg").strip(), pm.group("file"), pm.group("line")

    # 2) Python (Atheris): deepest frame that is NOT the fuzz harness.
    if not file:
        frames = [(m.group("file"), m.group("line"), m.group("fn") or "")
                  for m in _PYFRAME.finditer(text)]
        frames = [(f, l, fn) for (f, l, fn) in frames
                  if not any(h in f for h in _PY_HARNESS) and fn != "TestOneInput"]
        if frames:
            file, line = frames[-1][0], frames[-1][1]
            excs = list(_PYEXC.finditer(text))
            if excs:
                msg = f"{excs[-1].group('exc')}: {excs[-1].group('m')}".strip()

    # 3) JS/TS (Jazzer.js): shallowest user frame (the property/target body).
    if not file:
        frames = [(m.group("file"), m.group("line")) for m in _JSFRAME.finditer(text)]
        frames = [(f, l) for (f, l) in frames
                  if not any(s in f for s in _JS_SKIP) and ".fuzz." not in f]
        if frames:
            file, line = frames[0]
            em = _JSERR.search(text)
            if em:
                msg = em.group("m").strip()

    # 4) generic native frame.
    if not file:
        fm = _FRAME.search(text) or _SRC.search(text)
        if fm:
            file, line = fm.group(1), fm.group(2)

    if not file:
        return sarif  # crash with no locatable source frame

    props = {
        "waypoint_axes": ["logic", "edge-case"],
        "waypoint_hypothesis": "a fuzz-generated input reaches a panic/crash here — bound or validate the offending input, or handle the case",
    }
    repro = _reproducing_input(text)
    if repro:
        props["waypoint_reproducing_input"] = repro

    out.append(S.make_result(
        rule_id="fuzz/crash",
        level="error",
        message=f"Fuzzing found a crash/panic: {msg or 'crash'}",
        uri=file,
        start_line=int(line),
        properties=props,
    ))
    return sarif


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="fuzzer crash text ('-' = stdin)")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    sarif = convert(text)
    S.write_sarif(sarif, a.out)
    print(f"fuzz_to_sarif: {len(sarif['runs'][0]['results'])} crash(es) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
