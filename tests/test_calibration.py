"""Tests for per-rule precision calibration (verdict history -> score multiplier)."""
import json

import calibration as C
import sariflib as S
import rank as R
from conftest import beacon


def test_precision_neutral_with_no_data():
    assert abs(C.precision(0, 0, 4) - 0.5) < 1e-9      # Laplace -> neutral
    assert C.factor(0.5, 0.4, 1.3) == 1.0


def test_noisy_down_weighted_reliable_boosted():
    pn = C.precision(0, 9, 4)       # always dismissed
    pr = C.precision(9, 0, 4)       # always confirmed
    assert pn < 0.5 < pr
    assert C.factor(pn, 0.4, 1.3) < 1.0 < C.factor(pr, 0.4, 1.3)


def test_compute_and_factor_for():
    obs = {"r-noisy": {"confirm": 0, "dismiss": 10}, "r-good": {"confirm": 10, "dismiss": 0}}
    ccfg = {"enabled": True, "min_factor": 0.4, "max_factor": 1.3, "prior_strength": 4}
    calib = C.compute(obs, ccfg)
    assert calib["rules"]["r-noisy"]["factor"] < 1.0 < calib["rules"]["r-good"]["factor"]
    assert C.factor_for(["r-noisy"], calib, ccfg) < 1.0
    assert C.factor_for(["unknown"], calib, ccfg) == 1.0                 # no data -> neutral
    # a beacon with several contributing rules takes the most conservative factor
    assert C.factor_for(["r-noisy", "r-good"], calib, ccfg) == calib["rules"]["r-noisy"]["factor"]
    assert C.factor_for(["r-noisy"], calib, {"enabled": False}) == 1.0   # disabled -> neutral


def test_gather_from_verdicts(tmp_path):
    (tmp_path / "reports").mkdir()
    json.dump({"verdicts": [
        {"rule_id": "r1", "verdict": "dismiss", "content_hash": "h1"},
        {"rule_id": "r1", "verdict": "dismiss", "content_hash": "h2"},
        {"rule_id": "r1", "verdict": "confirm", "content_hash": "h3"},
        {"detectors": ["semgrep:r2"], "verdict": "confirm", "content_hash": "h4"},
    ]}, open(tmp_path / "reports" / "verdicts.json", "w"))
    cfg = {"dispatch": {"verdicts": "reports/verdicts.json"},
           "suppression": {"store": "suppression/store.json"}}
    obs = C.gather_observations(str(tmp_path), cfg)
    assert obs["r1"] == {"confirm": 1, "dismiss": 2}
    assert obs["r2"] == {"confirm": 1, "dismiss": 0}      # rule_id derived from detectors


def test_rank_applies_calibration(tmp_repo):
    """Two equal-prior beacons; the one whose rule was chronically dismissed must
    score lower after calibration — proving the loop actually reorders."""
    base = str(tmp_repo)
    good = beacon("svc.py", 2, axes=["security"], prior=0.6, rule="r-good", chash="g")
    noisy = beacon("svc.py", 2, axes=["security"], prior=0.6, rule="r-noisy", chash="n")
    sarif = S.empty_sarif("waypoint"); sarif["runs"][0]["results"] = [good, noisy]
    bpath = str(tmp_repo / "b.sarif"); S.write_sarif(sarif, bpath)
    calib = str(tmp_repo / "calib.json")
    json.dump({"version": 1, "rules": {"r-noisy": {"factor": 0.4}, "r-good": {"factor": 1.3}}},
              open(calib, "w"))
    out = str(tmp_repo / "ranked.sarif")
    R.main([bpath, "--suppress", str(tmp_repo / "s.json"), "--calibration", calib,
            "-o", out, "--suppressed-out", str(tmp_repo / "sup.sarif"), "--base", base])
    score = {b["properties"][S.WP]["rule_id"]: b["properties"][S.WP]["score"]
             for b in S.read_sarif(out)["runs"][0]["results"]}
    assert score["r-noisy"] < score["r-good"]
