"""Tests for the Waypoint MCP server (integrations/mcp/waypoint_mcp.py).

Exercises the tool logic + registration without standing up the stdio transport
(a live handshake is verified manually; here we keep it fast + deterministic).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integrations", "mcp"))
import waypoint_mcp as W  # noqa: E402


def test_four_tools_registered():
    names = set(W.mcp._tool_manager._tools.keys())
    assert {"waypoint_doctor", "waypoint_scan",
            "waypoint_beacons", "waypoint_dark_zone"} <= names


def test_beacons_parse(tmp_path):
    sarif = {"runs": [{"results": [
        {"ruleId": "R1",
         "properties": {"waypoint": {"rank": 1, "score": 1.9, "axes": ["security"],
                                     "hypothesis": "h", "boundary_reachable": True}},
         "locations": [{"physicalLocation": {"artifactLocation": {"uri": "a.py"},
                                             "region": {"startLine": 5}}}]},
    ]}]}
    p = tmp_path / "r.sarif"
    p.write_text(json.dumps(sarif), encoding="utf-8")
    out = W._beacons_from(p, 10)
    assert out and out[0]["file"] == "a.py" and out[0]["line"] == 5 and out[0]["rule"] == "R1"


def test_dark_zone_returns_only_observed_tiers(tmp_path):
    rep = {"gaps": [
        {"tier": "code-exec-adjacent", "file": "x.py", "line": 2},
        {"tier": "opaque", "file": "y.py", "line": 3},          # not graded → not returned
        {"tier": "sink-adjacent", "file": "z.py", "line": 4},
        {"tier": "unparsed", "file": "w.py", "line": 1},        # not graded → not returned
    ]}
    p = tmp_path / "b.json"
    p.write_text(json.dumps(rep), encoding="utf-8")
    out = W._dark_zone_from(p, 10)
    assert {g["file"] for g in out} == {"x.py", "z.py"}   # only observed-backed tiers


def test_scan_rejects_nonexistent_dir():
    assert "error" in W.op_scan("/no/such/dir/definitely/xyz")


def test_deep_tier_requires_trust(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    assert "trust=True" in W.op_scan(str(tmp_path), tier="deep").get("error", "")
