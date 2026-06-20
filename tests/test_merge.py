"""Tests for merge_sarif: tag resolution, dedup, relativize."""
import os

import sariflib as S
import merge_sarif as M
from conftest import raw_sarif, beacon


CONFIG = {"severity_prior_map": {"error": 0.9, "warning": 0.6, "note": 0.3, "none": 0.1}}
TAGMAP = S.load_yaml(os.path.join(S.repo_root(), "tag_map.yaml"))


def _norm(tool, result, base):
    run = raw_sarif(tool, [result])["runs"][0]
    return M.normalize_one(run, result, CONFIG, TAGMAP, base)


def test_axes_from_custom_metadata(tmp_repo):
    res = S.make_result("waypoint-py-async-shared-mutable", "warning", "race?", "app.py", 3,
                        properties={"waypoint_axes": ["concurrency", "abuse"],
                                    "waypoint_hypothesis": "data race?"})
    b = _norm("semgrep", res, str(tmp_repo))
    w = b["properties"][S.WP]
    assert w["axes"] == ["abuse", "concurrency"]      # sorted, both kept
    assert w["hypothesis"] == "data race?"


def test_axes_from_tag_map_bandit(tmp_repo):
    res = S.make_result("B608", "error", "sql", "app.py", 3)
    b = _norm("bandit", res, str(tmp_repo))
    assert set(b["properties"][S.WP]["axes"]) == {"security", "abuse"}


def test_axes_default_when_unknown(tmp_repo):
    res = S.make_result("ZZZ999", "warning", "?", "app.py", 3)
    b = _norm("some-unknown-tool", res, str(tmp_repo))
    assert b["properties"][S.WP]["axes"] == ["edge-case"]


def test_dedup_merges_overlapping_into_multi_axis(tmp_repo):
    base = str(tmp_repo)
    b1 = beacon("app.py", 3, 3, axes=["security"], rule="r-sql", chash="h1")
    b2 = beacon("app.py", 3, 4, axes=["concurrency"], rule="r-race", chash="h2")
    merged, stats = M.dedup([b1, b2], base)
    assert stats["out"] == 1
    w = merged[0]["properties"][S.WP]
    assert set(w["axes"]) == {"security", "concurrency"}      # union -> multi-axis
    assert len(w["merged_from"]) == 2                          # provenance preserved
    assert {m["rule_id"] for m in w["merged_from"]} == {"r-sql", "r-race"}


def test_dedup_keeps_distinct_regions_separate(tmp_repo):
    base = str(tmp_repo)
    b1 = beacon("app.py", 1, 1, axes=["security"], chash="a")
    b2 = beacon("svc.py", 5, 5, axes=["edge-case"], chash="b")
    merged, stats = M.dedup([b1, b2], base)
    assert stats["out"] == 2


def test_dedup_unlocated_by_hash(tmp_path):
    # dependency-CVE style beacons (no source region) dedup by content hash
    b1 = beacon("requirements.txt", 0, 0, axes=["security"], chash="cve-1")
    b2 = beacon("requirements.txt", 0, 0, axes=["security"], chash="cve-1")
    b3 = beacon("requirements.txt", 0, 0, axes=["security"], chash="cve-2")
    merged, stats = M.dedup([b1, b2, b3], str(tmp_path))
    assert stats["out"] == 2


def test_merged_hash_keyed_to_head_survives_partner_churn(tmp_repo):
    # The merged beacon must hash by the strongest member's OWN region, so a
    # dismissal still matches when a nearby detector later stops firing (#1).
    base = str(tmp_repo)
    head = beacon("app.py", 3, 3, axes=["security"], prior=0.9, chash="HEAD")
    partner = beacon("app.py", 3, 4, axes=["concurrency"], prior=0.6, chash="PART")
    merged, _ = M.dedup([head, partner], base)
    assert merged[0]["properties"][S.WP]["content_hash"] == "HEAD"
    # head alone (partner gone) yields the SAME hash -> suppression persists
    merged2, _ = M.dedup([head], base)
    assert merged2[0]["properties"][S.WP]["content_hash"] == "HEAD"


def test_malformed_properties_do_not_crash(tmp_repo):
    res = S.make_result("x", "warning", "m", "app.py", 3)
    res["properties"] = ["not", "a", "dict"]          # malformed SARIF
    b = _norm("semgrep", res, str(tmp_repo))           # must not raise
    assert b["properties"][S.WP]["axes"] == ["edge-case"]


def test_relativize_absolute_uri(tmp_repo):
    base = str(tmp_repo)
    abs_uri = os.path.join(base, "app.py")
    res = S.make_result("x", "warning", "m", abs_uri, 3)
    b = _norm("semgrep", res, base)
    assert S.result_location(b)["uri"] == "app.py"           # relativized for portability
