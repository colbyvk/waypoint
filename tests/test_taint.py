"""Regression test for the Semgrep taint-mode rules (free intra-file dataflow).

Runs the taint rules against the intentionally-vulnerable fixtures and asserts the
contract encoded in the fixtures themselves: every `WAYPOINT-PLANT` line (input
reaches a sink) fires, and every `WAYPOINT-OK` line (constant / parametrized /
sanitized) stays quiet. Needs semgrep — skipped if it isn't installed.
"""
import json
import os
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMGREP = os.path.join(ROOT, ".venv", "bin", "semgrep")

pytestmark = pytest.mark.skipif(not os.path.exists(SEMGREP), reason="semgrep not installed")


def _hits(rules_rel, fixture_rel):
    rules = os.path.join(ROOT, rules_rel)
    fx = os.path.join(ROOT, fixture_rel)
    out = subprocess.run([SEMGREP, "--config", rules, fx, "--json", "--metrics=off", "-q"],
                         capture_output=True, text=True, cwd=ROOT, timeout=180)
    data = json.loads(out.stdout or "{}")
    hit = {r["start"]["line"] for r in data.get("results", [])}
    src = open(fx, encoding="utf-8").read().splitlines()
    # a real marker is `WAYPOINT-PLANT: <rule-id>` (the colon excludes prose mentions
    # in the docstring) and sits on the line ABOVE the code it describes.
    plant = {i + 2 for i, ln in enumerate(src) if "WAYPOINT-PLANT:" in ln}
    ok = {i + 2 for i, ln in enumerate(src) if "WAYPOINT-OK:" in ln}
    return plant, ok, hit


def test_python_taint_fires_on_plant_only():
    plant, ok, hit = _hits("infra/core/python/security/python-taint.yaml",
                           "samples/monorepo/py_service/taint_samples.py")
    assert plant and plant <= hit, f"taint MISSED plant lines: {sorted(plant - hit)}"
    assert not (ok & hit), f"taint FIRED on safe (OK) lines: {sorted(ok & hit)}"


def test_ts_taint_fires_on_plant_only():
    plant, ok, hit = _hits("infra/core/typescript/security/typescript-taint.yaml",
                           "samples/monorepo/ts_lib/src/taint_samples.ts")
    assert plant and plant <= hit, f"taint MISSED plant lines: {sorted(plant - hit)}"
    assert not (ok & hit), f"taint FIRED on safe (OK) lines: {sorted(ok & hit)}"
