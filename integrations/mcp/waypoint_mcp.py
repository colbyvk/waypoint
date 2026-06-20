#!/usr/bin/env python3
"""
Waypoint MCP server — exposes Waypoint's triage to ANY MCP-capable agent
(Claude Code, Cursor, Gemini, ChatGPT/Codex, …) so a person can just say
"check my code with Waypoint" and the agent drives the whole tool. No flags,
no SARIF, no clone-and-symlink dance.

Run (under Waypoint's own venv, which has `mcp` installed):
    <waypoint>/.venv/bin/python integrations/mcp/waypoint_mcp.py
Register it with your agent via the repo's .mcp.json (see README → "Use it from
your agent").

Tools:
  waypoint_doctor()                     which detectors are active + what each gap costs
  waypoint_scan(path, tier, trust)      run a scan; returns counts + artifact paths
  waypoint_beacons(top)                 top-N ranked beacons (what it FOUND) to verify
  waypoint_dark_zone(top)               top-N ranked blind spots (what it COULDN'T verify)

Design: the server surfaces STRUCTURED findings; it never claims a beacon is a
confirmed bug. The agent reads the cited files itself, verifies, and reports —
exactly the workflow in skills/waypoint/SKILL.md.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]          # integrations/mcp/ -> <waypoint>
WP = ROOT / "bin" / "waypoint"
DOCTOR = ROOT / "detectors" / "doctor.sh"
RANKED = ROOT / "reports" / "ranked.sarif"
BLINDSPOTS = ROOT / "reports" / "blindspots.json"

mcp = FastMCP("waypoint")


# --------------------------------------------------------------------------- #
# plain logic (unit-testable without the MCP transport)
# --------------------------------------------------------------------------- #
def _run(args, timeout=1800):
    return subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)


def op_doctor() -> str:
    r = _run(["bash", str(DOCTOR)])
    return (r.stdout or "") + (("\n" + r.stderr) if r.stderr else "")


def _beacons_from(path: Path, top: int) -> list:
    try:
        sarif = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for run in sarif.get("runs", []):
        for res in run.get("results", []):
            wp = (res.get("properties") or {}).get("waypoint", {}) or {}
            loc = (((res.get("locations") or [{}])[0]).get("physicalLocation") or {})
            art = (loc.get("artifactLocation") or {}).get("uri", "")
            reg = loc.get("region") or {}
            out.append({
                "rank": wp.get("rank"),
                "score": wp.get("score"),
                "file": art,
                "line": reg.get("startLine"),
                "rule": res.get("ruleId"),
                "axes": wp.get("axes", []),
                "boundary_reachable": wp.get("boundary_reachable"),
                "hypothesis": wp.get("hypothesis", ""),
            })
    out.sort(key=lambda b: (b.get("score") or 0), reverse=True)
    return out[:top]


def op_beacons(top: int = 25) -> list:
    return _beacons_from(RANKED, top)


# Tiers backed by OBSERVED facts (a sink the parsed body calls / a computed-code
# dispatch). opaque/unparsed regions are NOT graded, so they aren't returned here —
# they're counted in blindspots.json. (Mirrors coverage.SHOWN_TIERS.)
_SHOWN_TIERS = ("code-exec-adjacent", "sink-adjacent")


def _dark_zone_from(path: Path, top: int) -> list:
    try:
        rep = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    gaps = [g for g in rep.get("gaps", []) if g.get("tier") in _SHOWN_TIERS]
    return gaps[:top]   # already ordered by observed facts in coverage.py


def op_dark_zone(top: int = 25) -> list:
    return _dark_zone_from(BLINDSPOTS, top)


def op_scan(path: str, tier: str = "fast", trust: bool = False) -> dict:
    p = os.path.abspath(os.path.expanduser(path or ""))
    if not os.path.isdir(p):
        return {"error": f"not a directory: {p}"}
    args = [str(WP), p]
    if tier == "changed":
        args.append("--changed")
    elif tier == "deep":
        if not trust:
            return {"error": "tier='deep' EXECUTES the target's own code (tests/fuzzers). "
                             "Pass trust=True only for code you trust, or use the sandbox "
                             "(bin/waypoint-sandboxed)."}
        args += ["--deep", "--i-trust-this-code"]
    elif tier != "fast":
        return {"error": f"unknown tier '{tier}' (use fast | changed | deep)"}
    r = _run(args)
    beacons = op_beacons(10000)
    dark = op_dark_zone(10000)
    return {
        "ok": r.returncode == 0,
        "tier": tier,
        "scanned": p,
        "beacon_count": len(beacons),
        "dark_zone_count": len(dark),
        "index_md": str(ROOT / "beacons" / "INDEX.md"),
        "blindspots_md": str(ROOT / "beacons" / "BLINDSPOTS.md"),
        "ranked_sarif": str(RANKED),
        "log_tail": (r.stdout or "").splitlines()[-12:],
        "next": "Call waypoint_beacons() and waypoint_dark_zone() for structured findings, "
                "then OPEN the cited file:line and verify each before reporting. You are the verifier.",
    }


# --------------------------------------------------------------------------- #
# MCP tool surface
# --------------------------------------------------------------------------- #
@mcp.tool()
def waypoint_doctor() -> str:
    """Report which Waypoint detectors are installed and what each MISSING one costs.
    Call this first. If it reports the CORE missing, tell the user to run detectors/install.sh."""
    return op_doctor()


@mcp.tool()
def waypoint_scan(path: str, tier: str = "fast", trust: bool = False) -> dict:
    """Scan a directory for security / correctness / concurrency / dependency / config issues.

    path : absolute path to the code to scan.
    tier : 'fast' (default — $0, seconds, NO target code executed) |
           'changed' (only files changed vs git) |
           'deep' (CodeQL cross-file taint + dynamic logic lane; EXECUTES target code — needs trust=True).
    Returns beacon + dark-zone counts and the artifact paths to read next."""
    return op_scan(path, tier, trust)


@mcp.tool()
def waypoint_beacons(top: int = 25) -> list:
    """Top-N ranked BEACONS from the last scan — what Waypoint FOUND (suspicions to verify),
    each with file, line, rule, axes, score, and a hypothesis to prove or disprove."""
    return op_beacons(top)


@mcp.tool()
def waypoint_dark_zone(top: int = 25) -> list:
    """Top-N ranked DARK-ZONE blind spots from the last scan — regions Waypoint COULD NOT verify
    (dynamic dispatch, framework/reflection-reached handlers, unparsed files), ranked by
    attack-surface relevance. Their silence is NOT safety: open each and answer its hypothesis."""
    return op_dark_zone(top)


if __name__ == "__main__":
    mcp.run()
