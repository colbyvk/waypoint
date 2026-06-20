"""Tests for emit_beacons.py — Waypoint drops .md beacons (path + classification)."""
import os

import sariflib as S
import emit_beacons as E
from conftest import beacon


def test_emits_index_and_per_beacon_md_with_path_and_classification(tmp_path):
    b = beacon("py_service/db.py", 17, axes=["security", "abuse"],
               rule="waypoint-py-sql-string-build", chash="abc1234567")
    b["properties"][S.WP]["rank"] = 1
    b["properties"][S.WP]["score"] = 1.42
    sarif = S.empty_sarif("waypoint-ranked")
    sarif["runs"][0]["results"] = [b]
    ranked = str(tmp_path / "ranked.sarif"); S.write_sarif(sarif, ranked)
    out_dir = str(tmp_path / "beacons"); index = str(tmp_path / "BEACONS.md")

    shown, total = E.emit(ranked, out_dir, index)
    assert shown == 1 and total == 1

    # the index carries the file path + classification
    idx = open(index, encoding="utf-8").read()
    assert "py_service/db.py:17" in idx
    assert "security, abuse" in idx
    assert "waypoint-py-sql-string-build" in idx

    # one per-beacon .md exists, with path + classification + why
    mds = [f for f in os.listdir(out_dir) if f.endswith(".md")]
    assert len(mds) == 1
    body = open(os.path.join(out_dir, mds[0]), encoding="utf-8").read()
    assert "**File:** `py_service/db.py:17`" in body
    assert "**Classification:** security, abuse" in body
    assert "Why this region was beaconed" in body


def test_redact_secrets_helper():
    assert "«redacted-secret»" in S.redact_secrets("aws key AKIAIOSFODNN7EXAMPLE")
    assert "«redacted-secret»" in S.redact_secrets("password = hunter2SuperSecret")
    assert S.redact_secrets("a1b2c3d4e5f6a1b2c3d4e5f6") == "a1b2c3d4e5f6a1b2c3d4e5f6"  # content hash survives
    assert S.redact_secrets("string-built SQL into execute()") == "string-built SQL into execute()"


def test_secret_values_are_redacted_in_beacon(tmp_path):
    b = beacon("config.py", 3, axes=["security"], rule="waypoint-py-hardcoded-secret",
               hypothesis="hardcoded credential: aws_secret_access_key = AKIAIOSFODNN7EXAMPLE",
               chash="s1")
    b["properties"][S.WP]["rank"] = 1
    sarif = S.empty_sarif("waypoint-ranked"); sarif["runs"][0]["results"] = [b]
    ranked = str(tmp_path / "r.sarif"); S.write_sarif(sarif, ranked)
    out_dir = str(tmp_path / "beacons"); index = str(tmp_path / "BEACONS.md")
    E.emit(ranked, out_dir, index)
    md = [f for f in os.listdir(out_dir) if f.endswith(".md")][0]
    body = open(os.path.join(out_dir, md), encoding="utf-8").read()
    assert "AKIAIOSFODNN7EXAMPLE" not in body          # the secret is never written out
    assert "«redacted-secret»" in body                  # masked instead
    assert "Sensitivity" in open(index, encoding="utf-8").read()   # INDEX warns


def test_stale_beacons_are_cleared(tmp_path):
    out_dir = str(tmp_path / "beacons"); os.makedirs(out_dir)
    open(os.path.join(out_dir, "9999_stale.md"), "w").write("old")
    sarif = S.empty_sarif("waypoint-ranked")
    sarif["runs"][0]["results"] = [beacon("a.py", 1, chash="h")]
    sarif["runs"][0]["results"][0]["properties"][S.WP]["rank"] = 1
    ranked = str(tmp_path / "r.sarif"); S.write_sarif(sarif, ranked)
    E.emit(ranked, out_dir, str(tmp_path / "BEACONS.md"))
    assert "9999_stale.md" not in os.listdir(out_dir)   # last run's beacons cleared


def test_top_n_cap_limits_human_output_but_not_sarif(tmp_path):
    sarif = S.empty_sarif("waypoint-ranked")
    results = []
    for i in range(5):
        b = beacon(f"f{i}.py", i + 1, chash=f"hash{i:07d}")
        b["properties"][S.WP]["rank"] = i + 1
        b["properties"][S.WP]["score"] = 5 - i          # f0 highest (5) … f4 lowest (1)
        results.append(b)
    sarif["runs"][0]["results"] = results
    ranked = str(tmp_path / "r.sarif"); S.write_sarif(sarif, ranked)
    out_dir = str(tmp_path / "b"); index = str(tmp_path / "I.md")

    shown, total = E.emit(ranked, out_dir, index, cap=2)
    assert (shown, total) == (2, 5)
    assert len([f for f in os.listdir(out_dir) if f.endswith(".md")]) == 2  # only top-2 .md
    idx = open(index, encoding="utf-8").read()
    assert "showing top 2 of 5" in idx.lower()
    assert "f0.py" in idx and "f1.py" in idx            # the two highest-scored
    assert "f4.py" not in idx                            # lowest dropped from human view
