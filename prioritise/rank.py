#!/usr/bin/env python3
"""
rank.py — Phase 3. Score, suppress, and order beacons (spec §7 + §9).

    score = severity_prior
          + multi_axis_bonus           (if the beacon has >1 axis; the strongest
                                         cheap signal of a real problem)
          + centrality_weight * normalized_caller_count
          + boundary_bonus             (if reachable from an input/trust boundary)

Before scoring, beacons matching an active suppression (dismissed-region hash) or
an allowlist entry are removed from the active set and written to a separate
file — so a dismissed beacon does NOT re-raise until its region changes or the
suppression expires.

This stage is deterministic; no agent is involved yet.

Usage:
  python prioritise/rank.py reports/beacons.sarif \
      [--suppress suppression/store.json] [--allowlist suppression/allowlist.yaml] \
      [-o reports/ranked.sarif] [--config waypoint.config.yaml] [--top-n N]
"""
from __future__ import annotations
import argparse, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suppress  # noqa: E402
import callgraph  # noqa: E402
import calibration  # noqa: E402

_SRC_EXT = (".py", ".rs", ".ts", ".tsx", ".js", ".jsx")


# --------------------------------------------------------------------------- #
# centrality — approximate caller count from the call graph (spec §7: "do not
# over-engineer this"). We count call sites of a region's enclosing symbol
# across the repo's source, minus its own definition.
# --------------------------------------------------------------------------- #
def build_corpus(base: str, exclude_globs: list[str]) -> str:
    chunks = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in
                   (".git", ".venv", "node_modules", "target", "reports", "__pycache__")]
        for fn in files:
            if not fn.endswith(_SRC_EXT):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, base)
            if S.glob_match_path(rel, exclude_globs):
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    chunks.append(fh.read())
            except OSError:
                continue
    return "\n".join(chunks)


def caller_count(symbol: str | None, corpus: str) -> int:
    if not symbol:
        return 0
    n = len(re.findall(r"\b" + re.escape(symbol) + r"\s*\(", corpus))
    return max(0, n - 1)  # subtract the definition itself


# --------------------------------------------------------------------------- #
# boundary reachability — cheap approximation (path glob / symbol pattern /
# decorator marker just above the region). The agent does the real proof.
# --------------------------------------------------------------------------- #
def is_boundary(base: str, beacon: dict, bcfg: dict) -> bool:
    import fnmatch
    loc = S.result_location(beacon)
    uri = (loc.get("uri") or "").replace("\\", "/")
    if S.glob_match_path(uri, bcfg.get("path_globs", [])):
        return True
    sym = S.result_symbol(beacon) or S.enclosing_symbol(base, loc)
    if sym:
        for pat in bcfg.get("symbol_patterns", []):
            if fnmatch.fnmatch(sym, pat):
                return True
    markers = bcfg.get("decorator_markers", [])
    if markers and loc.get("start_line"):
        path = S.resolve_path(uri, base)
        if path and os.path.isfile(path):
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    lines = fh.read().splitlines()
            except OSError:
                lines = []
            lo = max(0, loc["start_line"] - 4)
            window = "\n".join(lines[lo:loc["start_line"]])
            if any(m in window for m in markers):
                return True
    return False


def score_beacon(beacon: dict, scfg: dict, norm_caller: float, boundary: bool) -> float:
    w = beacon["properties"][S.WP]
    s = float(w.get("severity_prior", 0.0))
    n_axes = len(set(w.get("axes", [])))
    if n_axes > 1:
        extra = min(scfg.get("extra_axis_cap", 0.2),
                    scfg.get("extra_axis_step", 0.1) * (n_axes - 2))
        s += scfg.get("multi_axis_bonus", 0.5) + extra
    s += scfg.get("centrality_weight", 0.3) * norm_caller
    if boundary:
        s += scfg.get("boundary_bonus", 0.4)
    return round(s, 4)


def rule_ids_of(beacon: dict) -> list[str]:
    w = beacon["properties"][S.WP]
    ids = [w.get("rule_id")] + [m.get("rule_id") for m in w.get("merged_from", [])]
    return [r for r in ids if r]


# A finding in test/spec code is real, but it does not ship — so for a
# production-safety triage it ranks below findings in shipping code. We do not
# drop it (recall), we sink it. This is language-agnostic: it catches test noise
# from every tool (bandit, semgrep, etc.), complementing ruff's per-file-ignores.
_TEST_PATH_RX = re.compile(
    r"(^|/)(tests?|__tests__|testing|spec|specs)/"      # tests/ __tests__/ spec/ …
    r"|(^|/)test_[^/]+$|(^|/)[^/]*_test\.[^/]+$"        # test_x.py · x_test.go
    r"|\.(test|spec)\.[^/]+$"                           # x.test.ts · x.spec.tsx
    r"|(^|/)conftest\.py$",                             # pytest conftest
    re.IGNORECASE,
)

# Non-core paths: examples, docs, build/packaging scripts, benchmarks. A finding
# here is usually real but lives in code that doesn't ship to users — on a
# production-safety triage it ranks below shipping code. (Validation showed
# examples/ dominating Flask's top-10 and docs/extras/ httpie's.) Sunk, never dropped.
_NONCORE_PATH_RX = re.compile(
    r"(^|/)(examples?|docs?|demos?|extras?|scripts?|benchmarks?|bench)/",
    re.IGNORECASE,
)


def is_test_path(beacon: dict) -> bool:
    try:
        uri = beacon["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    except (KeyError, IndexError, TypeError):
        return False
    return bool(_TEST_PATH_RX.search(uri or ""))


def is_noncore_path(beacon: dict) -> bool:
    try:
        uri = beacon["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    except (KeyError, IndexError, TypeError):
        return False
    return bool(_NONCORE_PATH_RX.search(uri or ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rank + suppress beacons.")
    ap.add_argument("beacons", help="merged beacon SARIF (from merge_sarif.py)")
    ap.add_argument("--suppress", default=None, help="suppression store json")
    ap.add_argument("--allowlist", default=None, help="allowlist yaml")
    ap.add_argument("--calibration", default=None, help="per-rule precision calibration json")
    ap.add_argument("-o", "--out", default=None, help="ranked output SARIF")
    ap.add_argument("--suppressed-out", default=None, help="where suppressed beacons go")
    ap.add_argument("--config", default=None)
    ap.add_argument("--base", default=S.repo_root())
    ap.add_argument("--top-n", type=int, default=None, help="annotate top-N as dispatch candidates")
    a = ap.parse_args(argv)

    config = S.load_config(a.config)
    scfg = config.get("scoring", {})
    bcfg = config.get("boundary", {})
    supp_cfg = config.get("suppression", {})
    root = S.repo_root()
    store_path = a.suppress or os.path.join(root, supp_cfg.get("store", "suppression/store.json"))
    allow_path = a.allowlist or os.path.join(root, supp_cfg.get("allowlist", "suppression/allowlist.yaml"))
    calib_path = a.calibration or os.path.join(root, supp_cfg.get("calibration_store", "suppression/calibration.json"))
    ccfg = scfg.get("calibration", {})
    calib = calibration.load(calib_path)        # {} when no verdict history -> neutral
    out_path = a.out or os.path.join(root, "reports", "ranked.sarif")
    supp_out = a.suppressed_out or os.path.join(root, "reports", "suppressed.sarif")
    top_n = a.top_n if a.top_n is not None else config.get("dispatch", {}).get("budget_top_n", 25)

    sarif = S.read_sarif(a.beacons)
    runs = sarif.get("runs") or [{}]
    beacons = list((runs[0] or {}).get("results", []) or [])
    # rank consumes MERGED beacons; skip anything without the waypoint bag (e.g. a
    # raw per-tool SARIF passed by mistake) rather than crashing on it.
    kept = []
    for b in beacons:
        if (b.get("properties") or {}).get(S.WP) is None:
            print("rank: WARNING skipping a result with no waypoint metadata "
                  "(not produced by merge_sarif.py)", file=sys.stderr)
            continue
        kept.append(b)
    beacons = kept

    store = suppress.load_store(store_path)
    allowlist = suppress.load_allowlist(allow_path)
    for p in suppress.allowlist_problems(allowlist):
        print(f"rank: WARNING {p}", file=sys.stderr)

    # ---- suppression pass ----
    active, suppressed = [], []
    for b in beacons:
        w = b["properties"][S.WP]
        h = w.get("content_hash")
        ids = rule_ids_of(b)
        uri = S.result_location(b).get("uri", "")
        sm = suppress.match_store(h, store)
        am = suppress.match_allowlist(ids, uri, h, allowlist) if not sm else None
        if sm:
            w["suppressed"] = {"by": "store", "verdict": sm.get("verdict"),
                               "expiry": sm.get("expiry"), "note": sm.get("note", "")}
            suppressed.append(b)
        elif am:
            w["suppressed"] = {"by": "allowlist", "justification": am.get("justification"),
                               "expiry": am.get("expiry")}
            suppressed.append(b)
        else:
            active.append(b)

    # ---- scoring pass (active only) ----
    # Build a REAL call graph (caller→callee edges) for proven centrality
    # (distinct-caller fan-in) and proven reachability (BFS from trust-boundary
    # entrypoints). Fall back to the text-corpus count / glob heuristic when a
    # symbol isn't in the graph, so nothing regresses on unparsed files.
    exclude = config.get("centrality", {}).get("exclude_globs", [])
    corpus = build_corpus(a.base, exclude)
    cg = callgraph.build(a.base, exclude)
    reachable = cg.reachable_from(callgraph.boundary_entrypoints(cg, a.base, bcfg))

    metas = []  # (caller_count, source, graph_reachable, symbol) per active beacon
    for b in active:
        sym = S.result_symbol(b) or S.enclosing_symbol(a.base, S.result_location(b))
        if cg.defined(sym):
            cc, src = cg.fan_in(sym), "call-graph"
        else:
            cc, src = caller_count(sym, corpus), "text"
        metas.append((cc, src, bool(sym and sym in reachable), sym))
    max_cc = max((m[0] for m in metas), default=0)
    for b, (cc, src, greach, sym) in zip(active, metas):
        norm = (cc / max_cc) if max_cc else 0.0
        heuristic_bnd = is_boundary(a.base, b, bcfg)
        boundary = heuristic_bnd or greach          # graph proof OR cheap heuristic
        w = b["properties"][S.WP]
        w["centrality"] = {"caller_count": cc, "normalized": round(norm, 4), "source": src}
        w["boundary_reachable"] = boundary
        w["boundary_source"] = "call-graph" if greach else ("heuristic" if heuristic_bnd else None)
        # precision calibration: down-weight rules past verdicts kept dismissing,
        # boost ones that got confirmed (neutral factor 1.0 until history exists).
        fac = calibration.factor_for(rule_ids_of(b), calib, ccfg)
        # test/spec code is real but does not ship → sink it (configurable, never 0)
        tfac = float(scfg.get("test_path_factor", 0.25)) if is_test_path(b) else 1.0
        # non-core (examples/docs/scripts/…): real but doesn't ship → sink, don't drop
        nfac = float(scfg.get("noncore_path_factor", 0.35)) if is_noncore_path(b) else 1.0
        w["score"] = round(score_beacon(b, scfg, norm, boundary) * fac * tfac * nfac, 4)
        if fac != 1.0:
            w["calibration"] = {"factor": fac}
        if tfac != 1.0:
            w["test_path"] = True
        if nfac != 1.0:
            w["noncore_path"] = True

    active.sort(key=lambda b: (b["properties"][S.WP]["score"],
                               b["properties"][S.WP]["severity_prior"]), reverse=True)
    for i, b in enumerate(active, 1):
        w = b["properties"][S.WP]
        w["rank"] = i
        w["dispatch_candidate"] = i <= top_n

    # ---- write outputs ----
    out = S.empty_sarif("waypoint-ranked")
    out["runs"][0]["results"] = active
    out["runs"][0]["properties"] = {"waypoint_stage": "ranked", "active": len(active),
                                    "suppressed": len(suppressed), "top_n": top_n}
    S.write_sarif(out, out_path)

    sout = S.empty_sarif("waypoint-suppressed")
    sout["runs"][0]["results"] = suppressed
    S.write_sarif(sout, supp_out)

    # ---- run log ----
    print(f"rank: {len(beacons)} beacons -> {len(active)} active, {len(suppressed)} suppressed")
    print(f"  store={os.path.relpath(store_path, root)} ({len(store.get('suppressions', []))} entries), "
          f"allowlist={len(allowlist)} entries")
    print(f"  top {min(top_n, len(active))} dispatch candidates:")
    for b in active[:min(top_n, 10)]:
        w = b["properties"][S.WP]; loc = S.result_location(b)
        flags = []
        if len(set(w["axes"])) > 1:
            flags.append("multi-axis")
        if w.get("boundary_reachable"):
            flags.append("boundary" + ("[ok]" if w.get("boundary_source") == "call-graph" else "~"))
        if w["centrality"]["caller_count"]:
            flags.append(f"callers={w['centrality']['caller_count']}")
        print(f"    #{w['rank']:<2} score={w['score']:<5} {','.join(w['axes']):28s} "
              f"{loc['uri'].split('/')[-1]}:{loc['start_line']}  [{' '.join(flags)}]")
    print(f"  -> {os.path.relpath(out_path, root)}  (+ {os.path.relpath(supp_out, root)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
