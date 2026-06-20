#!/usr/bin/env python3
"""
coverage.py — the blind-spot map ("dark zone"), now with an honest epistemics.

Beacons say "here is what the deterministic pass FOUND". This says the opposite,
and more honestly: "here is what the pass COULD NOT REASON ABOUT — so its silence
there means nothing." The absence of a beacon is ambiguous: the code may be clean,
or the analyzer may simply not have seen it (dynamic dispatch, reflection,
framework-registered handlers, files it could not parse).

TWO honesty rules drive this module:

  1. We NEVER assign a severity score to a region we did not traverse. A region's
     placement comes ONLY from FACTS WE OBSERVED (did its parsed body call `exec`?
     a SQL sink?), expressed as a categorical TIER — not a fabricated number.
     Reachability is, by definition, UNRESOLVED for everything here.
       code-exec-adjacent  — we saw exec/eval/deser/computed-code in the body
       sink-adjacent       — we saw a sql/io/net sink in the body
       opaque              — computed dispatch / orphan, NO observed sink (not graded)
       unparsed            — we could not read it at all (graded NOTHING)
     Name-shape / boundary-path are weak HINTS that only break ties WITHIN a tier;
     they never define a tier (that would be "pretending to know").

  2. COVERAGE PARTITION (the guarantee): every enumerated function is either
     ANALYZED (parsed AND reachable from a trust-boundary entrypoint OR the public
     API surface, via RESOLVED calls) or DARK (everything else — all listed). `analyzed ∪ dark = all`,
     `analyzed ∩ dark = ∅`, asserted at runtime. The call graph is CONSERVATIVE:
     an unresolved/computed/mis-parsed edge is never used to mark a target
     reachable — we always err toward DARK. So nothing is silently assumed safe.
     (Sound enumeration for Python via `ast`; conservative best-effort for TS/Rust
     via the brace extractor — see GUARANTEES.md.)

Pure standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import callgraph  # noqa: E402
import sariflib as S  # noqa: E402

# Callee names that indicate a dangerous operation. Matched EXACTLY (case-insensitive)
# against last-component callee names (`subprocess.run` -> "run").
DEFAULT_SINKS = [
    "exec", "eval", "compile", "system", "popen", "Popen", "spawn", "fork",
    "check_output", "check_call", "call", "run",                     # subprocess
    "execute", "executemany", "executescript", "raw", "query",       # sql
    "loads", "load", "load_pem", "from_pickle", "unpickle",          # deserialize
    "open", "urlopen", "urlretrieve", "request", "get", "post", "connect", "send",  # io/net
    "render_template_string", "Markup", "innerHTML", "dangerouslySetInnerHTML",     # templating/xss
    "__import__", "import_module",                                   # reflection (computed import)
]

# Reaching one of THESE = arbitrary code / command / deserialization (→ RCE).
HIGH_SINKS = {
    "exec", "eval", "compile", "system", "popen", "spawn", "fork",
    "check_output", "check_call", "call", "run",
    "loads", "load", "load_pem", "from_pickle", "unpickle",
    "__import__", "import_module", "render_template_string", "markup",
}

# Dynamic-dispatch kinds that THEMSELVES execute computed code (observed fact).
EXEC_KINDS = {"eval", "exec", "compile", "function-ctor"}

# Tiers, strongest observed signal first. Only the first two are individually shown
# and ordered; opaque/unparsed are COUNTED, never graded (we didn't traverse them).
TIER_CODE_EXEC = "code-exec-adjacent"
TIER_SINK = "sink-adjacent"
TIER_OPAQUE = "opaque"
TIER_UNPARSED = "unparsed"
TIER_RANK = {TIER_CODE_EXEC: 0, TIER_SINK: 1, TIER_OPAQUE: 2, TIER_UNPARSED: 3}
SHOWN_TIERS = (TIER_CODE_EXEC, TIER_SINK)   # the observed-fact-backed tiers

# Name TOKENS that hint "untrusted input arrives here" — WEAK tie-breakers only.
DEFAULT_INPUT_SHAPES = [
    "handle", "handler", "route", "view", "endpoint", "controller", "dispatch",
    "on", "do", "parse", "load", "loads", "deserialize", "decode", "webhook",
    "callback", "command", "cmd", "process", "render", "serve",
]

# Test/spec files: their functions are runner-dispatched orphans, NOT attack surface.
_TEST_PATH_RX = re.compile(
    r"(^|/)(tests?|__tests__|testing|spec|specs)/"
    r"|(^|/)test_[^/]+$|(^|/)[^/]*_test\.[^/]+$"
    r"|\.(test|spec)\.[^/]+$|(^|/)conftest\.py$",
    re.IGNORECASE,
)
_TOKEN_RX = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")
# Vendored / generated code is not the user's own attack surface — excluded.
_VENDOR_PATH_RX = re.compile(
    r"(^|/)(node_modules|vendor|third_party|\.venv|site-packages|dist|build)/", re.IGNORECASE)
# Example / demo / sample code — real but low priority; a weak DE-prioritizing hint.
_DEMO_PATH_RX = re.compile(r"(^|/)(examples?|demos?|samples?|fixtures?)/", re.IGNORECASE)


def is_test_path(rel: str) -> bool:
    return bool(_TEST_PATH_RX.search((rel or "").replace("\\", "/")))


def is_vendor_path(rel: str) -> bool:
    return bool(_VENDOR_PATH_RX.search((rel or "").replace("\\", "/")))


def is_demo_path(rel: str) -> bool:
    return bool(_DEMO_PATH_RX.search((rel or "").replace("\\", "/")))


def _tokens(name: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RX.findall(name or "")}


def _cfg(covcfg: dict, key: str, default):
    v = covcfg.get(key)
    return v if v is not None else default


def _input_shaped(label: str, shapes) -> bool:
    toks = _tokens(label)
    return any(s.rstrip("_").lower() in toks for s in shapes)


def _sink_hits(callees, sinks) -> list[str]:
    sl = {s.lower() for s in sinks}
    return sorted({c for c in callees if c.lower() in sl})


def _sink_class(sink_hits) -> str | None:
    if any(h.lower() in HIGH_SINKS for h in sink_hits):
        return "code-exec"
    return "io-net" if sink_hits else None


def _tier(kind: str, sink_class: str | None, dynamic_kind: str | None) -> str:
    if kind in ("unparsed-file", "parse-incomplete"):
        return TIER_UNPARSED
    if sink_class == "code-exec" or (dynamic_kind in EXEC_KINDS):
        return TIER_CODE_EXEC
    if sink_class == "io-net":
        return TIER_SINK
    return TIER_OPAQUE


def gather(base: str, config: dict) -> dict:
    """Build the graph and return tiered blind spots + a coverage PARTITION."""
    covcfg = config.get("coverage", {}) or {}
    bcfg = config.get("boundary", {}) or {}
    sinks = _cfg(covcfg, "sinks", DEFAULT_SINKS)
    shapes = _cfg(covcfg, "input_shapes", DEFAULT_INPUT_SHAPES)
    exclude = (config.get("centrality", {}) or {}).get("exclude_globs", [])
    path_globs = bcfg.get("path_globs", []) or []

    cg = callgraph.build(base, exclude)
    roots = callgraph.boundary_entrypoints(cg, base, bcfg)
    reachable = cg.reachable_from(roots)

    def boundary_file(rel: str) -> bool:
        return S.glob_match_path((rel or "").replace("\\", "/"), path_globs)

    def in_scope(rel: str) -> bool:
        return not (is_test_path(rel) or is_vendor_path(rel))

    gaps = []

    def add(kind, file, line, name, enclosing, callees, dynamic_kind=None, base_reason=None):
        if not in_scope(file):
            return
        sink_hits = _sink_hits(callees, sinks)
        sink_class = _sink_class(sink_hits)
        tier = _tier(kind, sink_class, dynamic_kind)
        n_code_exec = sum(1 for h in sink_hits if h.lower() in HIGH_SINKS)
        if dynamic_kind in EXEC_KINDS:
            n_code_exec += 1
        observed = {"sinks": sink_hits, "sink_class": sink_class,
                    "dynamic_kind": dynamic_kind, "parsed": kind not in ("unparsed-file", "parse-incomplete")}
        # WEAK hints — never set the tier, only break ties within one.
        label = name or enclosing or os.path.basename(file)
        hints = []
        if _input_shaped(label, shapes):
            hints.append("input-shaped name")
        if boundary_file(file):
            hints.append("trust-boundary file")
        demo = is_demo_path(file)
        if demo:
            hints.append("example/demo path")
        # human reasons — OBSERVED facts first, then the explicit unknown.
        reasons = []
        if base_reason:
            reasons.append(base_reason)
        if sink_hits:
            reasons.append(("observed: reaches code-exec sink(s): " if sink_class == "code-exec"
                            else "observed: reaches sink(s): ") + ", ".join(sink_hits[:5]))
        if dynamic_kind:
            reasons.append(f"observed: computed `{dynamic_kind}` dispatch")
        reasons.append("reachability: UNRESOLVED (this is why it's dark)")
        gaps.append({
            "kind": kind, "file": file, "line": line, "name": name, "enclosing": enclosing,
            "tier": tier, "observed": observed, "reachability": "unresolved",
            "hints": hints, "reasons": reasons,
            "_sort": (TIER_RANK[tier], 1 if demo else 0, -n_code_exec, -len(sink_hits),
                      0 if dynamic_kind else 1, -len(hints), file, line),
            "hypothesis": _hypothesis(kind, file, line, name, enclosing, sink_hits, dynamic_kind),
        })

    # 1) dynamic-dispatch sites (dedupe by file:line, keep highest-priority kind)
    best_dyn = {}
    for d in cg.dynamic_sites:
        key = (d["file"], d["line"])
        prio = callgraph._DYN_PRIORITY.get(d["kind"], 0)
        if key not in best_dyn or prio > best_dyn[key][0]:
            best_dyn[key] = (prio, d)
    for _, d in best_dyn.values():
        add("dynamic-dispatch", d["file"], d["line"], None, d["enclosing"],
            cg.edges.get(d["enclosing"], set()), dynamic_kind=d["kind"],
            base_reason="control flow is computed here — the graph cannot follow it")

    # 2) orphan callables — defined, zero in-graph callers, not an entrypoint
    for name, sites in cg.defs.items():
        if name == callgraph.TOPLEVEL or name in roots or cg.fan_in(name) > 0:
            continue
        site = sites[0]
        add("orphan-callable", site["file"], site["line"], name, None,
            cg.edges.get(name, set()),
            base_reason="no caller in the static graph — reached dynamically or dead")

    # 3) parse-incomplete (clike body we could not reliably bound) + unparsed files
    for pi in cg.parse_incomplete:
        add("parse-incomplete", pi["file"], pi.get("line", 1), pi.get("name"), None, set(),
            base_reason="parser could not reliably bound this function — treated as dark")
    for pf in cg.parse_failures:
        add("unparsed-file", pf["file"], 1, None, None, set(),
            base_reason="analyzer could not parse this file — ZERO coverage")

    gaps.sort(key=lambda g: g["_sort"])
    for g in gaps:
        del g["_sort"]   # internal only; never emitted (it is not a severity)

    # ---- COVERAGE PARTITION (the guarantee) --------------------------------
    funcs = {n for n, sites in cg.defs.items()
             if n != callgraph.TOPLEVEL and in_scope(sites[0]["file"])}
    analyzed = {n for n in funcs if n in reachable}     # parsed AND reachable via resolved edges
    dark = funcs - analyzed                              # everything else — never silently "clean"
    partition_holds = (analyzed | dark == funcs) and not (analyzed & dark)
    assert partition_holds, "coverage partition violated (analyzed ∪ dark ≠ all)"

    summary = {
        "code_files": cg.code_files,
        "functions": len(funcs),
        "analyzed": len(analyzed),
        "dark": len(dark),
        "graph_traceability_pct": round(100.0 * len(analyzed) / len(funcs), 1) if funcs else None,
        "unparsed_files": sum(1 for g in gaps if g["kind"] == "unparsed-file"),
        "parse_incomplete": sum(1 for g in gaps if g["kind"] == "parse-incomplete"),
        "partition_holds": partition_holds,
        "tiers": {t: sum(1 for g in gaps if g["tier"] == t)
                  for t in (TIER_CODE_EXEC, TIER_SINK, TIER_OPAQUE, TIER_UNPARSED)},
    }
    return {"version": 2, "summary": summary, "gaps": gaps}


def _hypothesis(kind, file, line, name, enclosing, sinks, dynamic_kind) -> str:
    where = f"{file}:{line}"
    sinkstr = ", ".join(sinks[:3]) if sinks else None
    if kind == "dynamic-dispatch":
        h = f"Dynamic dispatch at {where}"
        if enclosing and enclosing != callgraph.TOPLEVEL:
            h += f" in `{enclosing}()`"
        h += ". Trace whether attacker-controlled input can determine what is called/executed here"
        if sinkstr:
            h += f" — this path also reaches {sinkstr}"
        return h + " (RCE / injection / SSRF)?"
    if kind == "orphan-callable":
        h = f"`{name}()` ({where}) has no caller in the static graph"
        if sinkstr:
            h += f" yet reaches {sinkstr}"
        h += ". Determine HOW it is invoked (framework route, registration, reflection, event) " \
             "and whether untrusted input can reach it"
        return h + (f" and {sinkstr}?" if sinkstr else " — or confirm it is dead code?")
    if kind == "parse-incomplete":
        return (f"{where} could not be reliably parsed; its calls are unknown. Read it manually "
                "and confirm what it invokes / whether untrusted input reaches it.")
    if kind == "unparsed-file":
        return (f"{file} could not be parsed, so NOTHING in it was analyzed. Review it manually "
                "for injection / auth / secrets.")
    return f"Unverified region at {where}."


_KIND_LABEL = {
    "dynamic-dispatch": "Dynamic dispatch", "orphan-callable": "Orphan callable",
    "parse-incomplete": "Parse-incomplete", "unparsed-file": "Unparsed file",
}


def render_md(report: dict, top_k: int) -> str:
    s = report["summary"]
    shown = [g for g in report["gaps"] if g["tier"] in SHOWN_TIERS][:top_k]
    n_shown_tier = sum(s["tiers"][t] for t in SHOWN_TIERS)
    out = ["# Waypoint — blind-spot map (dark zone)", ""]
    out.append("> Regions the deterministic pass **could not reason about** — so the absence of a "
               "beacon here is *not* evidence of safety. **Ordered by what we OBSERVED adjacent** "
               "(a sink the parsed body calls, a computed dispatch); **reachability is unknown by "
               "definition.** We do **not** assign a severity to regions we did not traverse.")
    out.append("")
    # the partition guarantee, stated every run
    out.append(f"- **Coverage partition:** {s['functions']} functions — **{s['analyzed']} analyzed** "
               f"(parsed + reachable), **{s['dark']} dark** (all accounted for below or in "
               f"`blindspots.json`). `analyzed ∪ dark = all` · nothing silently assumed safe.")
    tr = s.get("graph_traceability_pct")
    if tr is not None:
        out.append(f"- **Traceability ≈ {tr}%** _(reachable from a trust-boundary entrypoint "
                   f"or the public API surface, via resolved calls)._")
    out.append(f"- **Could not even read:** {s['unparsed_files']} unparsed file(s), "
               f"{s['parse_incomplete']} parse-incomplete region(s) — graded NOTHING (we didn't traverse them).")
    out.append("")
    if shown:
        out.append("### Observed attack-surface-adjacent (ranked by observed facts, not severity)")
        out.append("")
        out.append("| # | tier | observed | location | reachability |")
        out.append("|--:|:--|:--|:--|:--|")
        for i, g in enumerate(shown, 1):
            loc = f"`{g['file']}:{g['line']}`" + (
                f" · `{g['name']}()`" if g["name"] else
                (f" · in `{g['enclosing']}()`" if g["enclosing"] and g["enclosing"] != callgraph.TOPLEVEL else ""))
            obs = ", ".join(g["observed"]["sinks"][:4]) or (g["observed"]["dynamic_kind"] or "—")
            if g["observed"]["dynamic_kind"] and g["observed"]["sinks"]:
                obs = f"{g['observed']['dynamic_kind']} → {obs}"
            hint = f" · _hint: {', '.join(g['hints'])}_" if g["hints"] else ""
            out.append(f"| {i} | {g['tier']} | {obs}{hint} | {loc} | **UNRESOLVED** |")
        out.append("")
        out.append("## Investigation hypotheses")
        for i, g in enumerate(shown, 1):
            out.append(f"{i}. {g['hypothesis']}")
        out.append("")
    else:
        out.append("_No regions with an observed attack-surface-adjacent fact._")
        out.append("")
    # opaque + unparsed: COUNTED, never individually graded
    n_opaque = s["tiers"][TIER_OPAQUE]
    n_unparsed_tier = s["tiers"][TIER_UNPARSED]
    out.append(f"> **Not ranked (no observed signal — we do not grade the un-traversed):** "
               f"{n_opaque} opaque region(s) (computed dispatch / orphans with no observed sink) and "
               f"{n_unparsed_tier} unparsed / parse-incomplete region(s). Full list in "
               f"`reports/blindspots.json`. Showing {len(shown)} of {n_shown_tier} observed-adjacent.")
    out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive Waypoint blind spots (the dark zone) — tiered by OBSERVED facts.")
    ap.add_argument("base", help="directory that was scanned")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out", default=None, help="blindspots.json path")
    ap.add_argument("--md", default=None, help="BLINDSPOTS.md path")
    ap.add_argument("--top-k", type=int, default=None)
    a = ap.parse_args(argv)

    root = S.repo_root()
    config = S.load_config(a.config)
    covcfg = config.get("coverage", {}) or {}
    top_k = a.top_k if a.top_k is not None else int(covcfg.get("top_k", 25))

    report = gather(a.base, config)
    out_json = a.out or os.path.join(root, "reports", "blindspots.json")
    out_md = a.md or os.path.join(root, "beacons", "BLINDSPOTS.md")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    json.dump(report, open(out_json, "w", encoding="utf-8"), indent=2)
    open(out_md, "w", encoding="utf-8").write(render_md(report, top_k))

    s = report["summary"]
    shown = len([g for g in report["gaps"] if g["tier"] in SHOWN_TIERS][:top_k])
    print(f"coverage: partition {s['analyzed']} analyzed / {s['dark']} dark of {s['functions']} fns "
          f"(traceability≈{s.get('graph_traceability_pct')}%, holds={s['partition_holds']})  "
          f"dark zone: {s['tiers'][TIER_CODE_EXEC]} code-exec, {s['tiers'][TIER_SINK]} sink, "
          f"{s['tiers'][TIER_OPAQUE]} opaque, {s['unparsed_files']}+{s['parse_incomplete']} unreadable "
          f"-> {shown} shown -> {os.path.relpath(out_md, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
