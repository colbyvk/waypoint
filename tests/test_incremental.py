"""Tests for incremental.py — splice a changed-files scan into a cached baseline."""
import incremental as I
import sariflib as S
from conftest import beacon


def _sarif(tmp, name, results):
    s = S.empty_sarif("waypoint"); s["runs"][0]["results"] = results
    p = str(tmp / name); S.write_sarif(s, p); return p


def test_combine_keeps_unchanged_drops_changed(tmp_path):
    base = str(tmp_path)
    baseline = [beacon("a.py", 1, chash="old-a"), beacon("b.py", 2, chash="b1")]
    fresh = [beacon("a.py", 1, chash="new-a")]          # a.py was re-scanned
    out = I.combine(fresh, baseline, ["a.py"], base)
    hashes = {b["properties"][S.WP]["content_hash"] for b in out}
    assert "new-a" in hashes        # fresh a.py kept
    assert "old-a" not in hashes    # stale baseline a.py dropped (file changed)
    assert "b1" in hashes           # unchanged b.py preserved from baseline
    assert len(out) == 2


def test_combine_empty_fresh_returns_baseline(tmp_path):
    base = str(tmp_path)
    baseline = [beacon("a.py", 1, chash="a1"), beacon("b.py", 2, chash="b1")]
    assert len(I.combine([], baseline, [], base)) == 2   # nothing changed -> full baseline


def test_main_writes_combined(tmp_path):
    base = str(tmp_path)
    fresh = _sarif(tmp_path, "fresh.sarif", [beacon("a.py", 1, chash="fa")])
    bl = _sarif(tmp_path, "baseline.sarif",
                [beacon("a.py", 1, chash="ba"), beacon("c.py", 3, chash="c1")])
    changed = str(tmp_path / "changed.txt"); open(changed, "w").write("a.py\n")
    out = str(tmp_path / "combined.sarif")
    I.main([fresh, "--baseline", bl, "--changed", changed, "-o", out, "--base", base])
    h = {b["properties"][S.WP]["content_hash"] for b in S.read_sarif(out)["runs"][0]["results"]}
    assert h == {"fa", "c1"}        # fresh a.py + baseline c.py; stale baseline a.py dropped
