"""Tests for trufflehog JSONL → SARIF normalization (verified-secrets lane)."""
import json
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "detectors", "normalize"))
sys.path.insert(0, os.path.join(_root, "detectors"))
import trufflehog_to_sarif as T  # noqa: E402
import sariflib as S  # noqa: E402


def test_verified_secret_becomes_error_beacon_and_never_leaks_value():
    jsonl = [
        json.dumps({"DetectorName": "AWS", "Verified": True, "Raw": "AKIAEXAMPLESECRET",
                    "SourceMetadata": {"Data": {"Filesystem": {"file": "app/config.py", "line": 12}}}}),
        json.dumps({"DetectorName": "Slack", "Verified": False, "Raw": "xoxb-nope",
                    "SourceMetadata": {"Data": {"Filesystem": {"file": "x.py", "line": 3}}}}),
        "",  # blank line tolerated
    ]
    sarif, n = T.convert(jsonl)
    assert n == 2
    res = sarif["runs"][0]["results"]
    aws = next(r for r in res if r["ruleId"] == "trufflehog-AWS")
    assert aws["level"] == "error"                                 # verified → high
    assert "AKIAEXAMPLESECRET" not in json.dumps(aws)             # secret value NEVER written
    assert aws["properties"]["waypoint_axes"] == ["abuse", "security"]
    loc = S.result_location(aws)
    assert loc["uri"] == "app/config.py" and loc["start_line"] == 12
    slack = next(r for r in res if r["ruleId"] == "trufflehog-Slack")
    assert slack["level"] == "warning"                            # unverified → lower


def test_garbage_and_non_finding_lines_ignored():
    _, n = T.convert(["not json at all", "{}", json.dumps({"no": "detector"})])
    assert n == 0
