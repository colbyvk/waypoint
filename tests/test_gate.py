"""Tests for the policy gate (prioritise/gate.py)."""
import sariflib as S
import gate as G
from conftest import beacon


GATE = {"fail_on_axes": ["security", "pit"], "min_severity_prior": 0.9,
        "fail_on_levels": ["error"], "only_confirmed": False, "max_violations": 0}


def test_violation_by_axis_and_prior():
    b = beacon("a.py", 1, axes=["security"], prior=0.9)
    assert G.is_violation(b, GATE, {}) is True


def test_no_violation_when_axis_not_a_blocker():
    b = beacon("a.py", 1, axes=["edge-case"], prior=0.95, level="error")
    assert G.is_violation(b, GATE, {}) is False        # edge-case isn't a blocker axis


def test_no_violation_when_not_serious_enough():
    b = beacon("a.py", 1, axes=["pit"], prior=0.6, level="note")
    assert G.is_violation(b, GATE, {}) is False         # below prior + not error level


def test_violation_by_error_level_even_if_low_prior():
    b = beacon("a.py", 1, axes=["pit"], prior=0.3, level="error")
    assert G.is_violation(b, GATE, {}) is True


def test_suppressed_beacon_never_violates():
    b = beacon("a.py", 1, axes=["security"], prior=0.95)
    b["properties"][S.WP]["suppressed"] = {"by": "store"}
    assert G.is_violation(b, GATE, {}) is False


def test_only_confirmed_requires_agent_verdict():
    g = {**GATE, "only_confirmed": True}
    b = beacon("a.py", 1, axes=["security"], prior=0.95, chash="h9")
    assert G.is_violation(b, g, {}) is False                    # no verdict yet
    assert G.is_violation(b, g, {"h9": "confirm"}) is True      # agent confirmed
    assert G.is_violation(b, g, {"h9": "dismiss"}) is False     # agent dismissed


def test_gate_main_fails_on_violation(tmp_path):
    s = S.empty_sarif("waypoint-ranked")
    s["runs"][0]["results"] = [beacon("a.py", 1, axes=["security"], prior=0.9)]
    p = str(tmp_path / "ranked.sarif"); S.write_sarif(s, p)
    assert G.main([p, "--force"]) == 1                  # 1 violation > max_violations=0


def test_gate_main_passes_when_clean(tmp_path):
    s = S.empty_sarif("waypoint-ranked")
    s["runs"][0]["results"] = [beacon("a.py", 1, axes=["edge-case"], prior=0.3, level="note")]
    p = str(tmp_path / "ranked.sarif"); S.write_sarif(s, p)
    assert G.main([p, "--force"]) == 0


def test_gate_disabled_without_force(tmp_path, capsys):
    s = S.empty_sarif("waypoint-ranked")
    s["runs"][0]["results"] = [beacon("a.py", 1, axes=["security"], prior=0.95)]
    p = str(tmp_path / "ranked.sarif"); S.write_sarif(s, p)
    assert G.main([p]) == 0                             # gate.enabled is false by default
