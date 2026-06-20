"""Tests for rank.py (scoring, centrality, boundary) and suppress.py."""
import datetime as dt
import json
import os

import sariflib as S
import rank as R
import suppress
from conftest import beacon

SCFG = {"multi_axis_bonus": 0.5, "centrality_weight": 0.3, "boundary_bonus": 0.4,
        "extra_axis_step": 0.1, "extra_axis_cap": 0.2}


# ---- scoring formula (spec §7) -------------------------------------------- #
def test_score_single_axis_is_just_prior():
    b = beacon("app.py", 1, axes=["security"], prior=0.6)
    assert R.score_beacon(b, SCFG, norm_caller=0.0, boundary=False) == 0.6


def test_score_multi_axis_bonus():
    b = beacon("app.py", 1, axes=["security", "abuse"], prior=0.6)
    assert R.score_beacon(b, SCFG, 0.0, False) == 0.6 + 0.5


def test_score_three_axes_adds_capped_extra():
    b = beacon("app.py", 1, axes=["security", "abuse", "concurrency"], prior=0.6)
    # +0.5 base multi-axis +0.1 for the third axis
    assert abs(R.score_beacon(b, SCFG, 0.0, False) - (0.6 + 0.5 + 0.1)) < 1e-9


# ---- non-core / test path down-weight (rank below shipping code) ---------- #
def test_noncore_path_detects_non_shipping_dirs():
    for p in ["examples/app.py", "docs/conf.py", "scripts/build.py",
              "extras/x.py", "benchmarks/b.py", "demos/d.ts", "a/examples/b.py"]:
        assert R.is_noncore_path(beacon(p, 1)), p


def test_noncore_path_ignores_shipping_code():
    for p in ["src/flask/app.py", "httpie/core.py", "lib/handler.ts", "documents.py"]:
        assert not R.is_noncore_path(beacon(p, 1)), p


def test_test_path_detected_and_distinct_from_shipping():
    assert R.is_test_path(beacon("tests/test_app.py", 1))
    assert R.is_test_path(beacon("pkg/x.test.ts", 1))
    assert not R.is_test_path(beacon("src/app.py", 1))


def test_score_boundary_and_centrality():
    b = beacon("app.py", 1, axes=["security"], prior=0.5)
    s = R.score_beacon(b, SCFG, norm_caller=1.0, boundary=True)
    assert abs(s - (0.5 + 0.3 * 1.0 + 0.4)) < 1e-9


# ---- centrality approximation --------------------------------------------- #
def test_caller_count(tmp_repo):
    corpus = R.build_corpus(str(tmp_repo), [])
    # `lookup(` appears 4× (1 def + 3 call sites: app.py:4, svc.py:5 ×2); minus
    # the definition -> 3 callers.
    assert R.caller_count("lookup", corpus) == 3
    assert R.caller_count("handle_request", corpus) == 0


# ---- boundary detection --------------------------------------------------- #
def test_is_boundary_by_symbol(tmp_repo):
    cfg = S.load_config()
    b = beacon("app.py", 3, axes=["security"])          # enclosing symbol handle_request
    assert R.is_boundary(str(tmp_repo), b, cfg["boundary"]) is True


def test_is_not_boundary(tmp_repo):
    cfg = S.load_config()
    b = beacon("svc.py", 2, axes=["edge-case"])          # enclosing symbol lookup
    assert R.is_boundary(str(tmp_repo), b, cfg["boundary"]) is False


# ---- suppression store ---------------------------------------------------- #
def test_match_store_respects_expiry_and_verdict():
    today = dt.date(2026, 6, 16)
    store = {"suppressions": [
        {"content_hash": "h-active", "verdict": "dismiss", "expiry": "2026-12-31"},
        {"content_hash": "h-expired", "verdict": "dismiss", "expiry": "2026-01-01"},
        {"content_hash": "h-confirm", "verdict": "confirm", "expiry": "2026-12-31"},
    ]}
    assert suppress.match_store("h-active", store, today) is not None
    assert suppress.match_store("h-expired", store, today) is None      # expired -> re-raise
    assert suppress.match_store("h-confirm", store, today) is None      # confirms never suppress


def test_record_dismissals_sets_expiry(tmp_path):
    path = str(tmp_path / "store.json")
    today = dt.date(2026, 6, 16)
    suppress.record_dismissals(path, [{"content_hash": "h1", "verdict": "dismiss"}],
                               default_expiry_days=90, ref=today)
    store = suppress.load_store(path)
    assert store["suppressions"][0]["expiry"] == "2026-09-14"


# ---- allowlist ------------------------------------------------------------ #
def test_allowlist_match_and_validation():
    today = dt.date(2026, 6, 16)
    good = [{"rule_id": "waypoint-py-*", "path": "**/util.py",
             "justification": "reviewed", "expiry": "2027-01-01"}]
    assert suppress.match_allowlist(["waypoint-py-path-traversal"], "src/util.py", "h",
                                    good, today) is not None
    # wrong path -> no match
    assert suppress.match_allowlist(["waypoint-py-path-traversal"], "src/db.py", "h",
                                    good, today) is None


def test_allowlist_invalid_entries_never_suppress():
    today = dt.date(2026, 6, 16)
    bad = [{"rule_id": "*", "path": "*"}]               # missing justification + expiry
    assert suppress.allowlist_problems(bad)             # reported
    assert suppress.match_allowlist(["anything"], "any.py", "h", bad, today) is None


def test_allowlist_bare_mapping_does_not_crash(tmp_path):
    # a single entry written at the YAML root (a common mistake) must load as a
    # one-element list, not crash rank on startup (#5)
    p = str(tmp_path / "allow.yaml")
    open(p, "w").write("rule_id: foo\njustification: x\nexpiry: '2027-01-01'\n")
    al = suppress.load_allowlist(p)
    assert isinstance(al, list) and al and al[0]["rule_id"] == "foo"
    assert suppress.allowlist_problems(al) == []        # iterating it is safe


def test_rank_skips_results_without_waypoint_bag(tmp_repo, capsys):
    base = str(tmp_repo)
    good = beacon("app.py", 3, axes=["security"], prior=0.6, chash="g")
    raw = S.make_result("X", "warning", "m", "app.py", 1)   # no waypoint bag
    sarif = S.empty_sarif("waypoint"); sarif["runs"][0]["results"] = [good, raw]
    bpath = str(tmp_repo / "b.sarif"); S.write_sarif(sarif, bpath)
    out = str(tmp_repo / "ranked.sarif")
    R.main([bpath, "--suppress", str(tmp_repo / "s.json"), "-o", out,
            "--suppressed-out", str(tmp_repo / "sup.sarif"), "--base", base])
    assert len(S.read_sarif(out)["runs"][0]["results"]) == 1   # raw result skipped


def test_rank_empty_runs_does_not_crash(tmp_path):
    sarif = {"version": "2.1.0", "runs": []}
    bpath = str(tmp_path / "b.sarif"); S.write_sarif(sarif, bpath)
    out = str(tmp_path / "ranked.sarif")
    assert R.main([bpath, "--suppress", str(tmp_path / "s.json"), "-o", out,
                   "--suppressed-out", str(tmp_path / "sup.sarif"),
                   "--base", str(tmp_path)]) == 0
    assert S.read_sarif(out)["runs"][0]["results"] == []


# ---- end-to-end rank + suppress ------------------------------------------- #
def test_rank_main_orders_and_suppresses(tmp_repo, capsys):
    base = str(tmp_repo)
    beacons = [
        beacon("svc.py", 2, axes=["edge-case"], prior=0.3, chash="low"),
        beacon("app.py", 3, axes=["security", "abuse"], prior=0.9, chash="high"),
        beacon("app.py", 4, axes=["security"], prior=0.6, chash="dismissed"),
    ]
    sarif = S.empty_sarif("waypoint")
    sarif["runs"][0]["results"] = beacons
    bpath = str(tmp_repo / "beacons.sarif"); S.write_sarif(sarif, bpath)

    store = str(tmp_repo / "store.json")
    suppress.save_store(store, {"version": 1, "suppressions": [
        {"content_hash": "dismissed", "verdict": "dismiss", "expiry": "2099-01-01"}]})
    allow = str(tmp_repo / "allow.yaml")
    open(allow, "w").write("allow: []\n")
    out = str(tmp_repo / "ranked.sarif"); sout = str(tmp_repo / "supp.sarif")

    R.main([bpath, "--suppress", store, "--allowlist", allow, "-o", out,
            "--suppressed-out", sout, "--base", base])

    ranked = S.read_sarif(out)["runs"][0]["results"]
    assert len(ranked) == 2                              # one was suppressed
    assert ranked[0]["properties"][S.WP]["content_hash"] == "high"   # top score first
    assert ranked[0]["properties"][S.WP]["rank"] == 1
    supp = S.read_sarif(sout)["runs"][0]["results"]
    assert len(supp) == 1 and supp[0]["properties"][S.WP]["content_hash"] == "dismissed"
