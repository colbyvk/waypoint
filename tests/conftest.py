"""Shared pytest fixtures + builders.

These tests exercise ONLY Waypoint's custom Python (sariflib, merge_sarif, rank,
suppress, dispatcher) using crafted SARIF + a tiny temp source tree. They do not
require any external scanner — that is the point: the custom surface must be
verifiable by the owning team without debugging a third-party engine.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("detectors", "prioritise", "dispatch"):
    p = os.path.join(ROOT, _d)
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def tmp_repo(tmp_path):
    """A minimal repo: app.py calls lookup(); svc.py defines + calls it twice."""
    (tmp_path / "app.py").write_text(
        "def handle_request(req):\n"          # 1  boundary-ish symbol name
        "    cache = {}\n"                     # 2
        "    cache[req] = 1\n"                 # 3  region of interest
        "    return lookup(req)\n",            # 4
        encoding="utf-8",
    )
    (tmp_path / "svc.py").write_text(
        "def lookup(x):\n"                     # 1
        "    return x\n"                       # 2
        "\n"                                   # 3
        "def caller():\n"                      # 4
        "    return lookup(1) + lookup(2)\n",  # 5  two call sites of lookup
        encoding="utf-8",
    )
    return tmp_path


def raw_result(rule_id, uri, start, end=None, level="warning", message="m",
               properties=None):
    """A single SARIF result as a raw tool would emit it."""
    import sariflib as S
    return S.make_result(rule_id, level, message, uri, start, end, properties=properties)


def raw_sarif(tool, results):
    """A per-tool SARIF log wrapping the given result dicts."""
    import sariflib as S
    s = S.empty_sarif(tool)
    s["runs"][0]["results"] = results
    return s


def beacon(uri, start, end=None, axes=("security",), rule="waypoint-x", tool="semgrep",
         level="warning", prior=0.6, hypothesis="confirm or deny", chash="hash0001",
         merged=None, subtags=()):
    """A merged-beacon result (post merge_sarif) for rank/dispatch tests."""
    import sariflib as S
    res = S.make_result(rule, level, "msg", uri, start, end)
    res["properties"] = {S.WP: {
        "axes": list(axes), "subtags": list(subtags), "severity_prior": prior,
        "hypothesis": hypothesis, "content_hash": chash, "tool": tool, "rule_id": rule,
        "merged_from": merged or [{"tool": tool, "rule_id": rule, "level": level, "message": "msg"}],
    }}
    return res
