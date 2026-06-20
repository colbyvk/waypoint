#!/usr/bin/env python3
"""
gate.py — the policy gate (the "teeth").

Exits non-zero when active beacons violate the policy in waypoint.config.yaml
(`gate:`), so CI can FAIL a pull request or block a deploy on the findings that
matter — instead of beacons being merely advisory. Deterministic; reads the ranked
beacons (and, optionally, agent verdicts) and applies a simple, explainable policy.

A beacon is a VIOLATION when:
    axis in fail_on_axes           (empty list = any axis counts)
  AND (severity_prior >= min_severity_prior  OR  level in fail_on_levels)
  AND (not only_confirmed  OR  an agent verdict == "confirm" for it)
The run fails when violation_count > max_violations.

Usage:
  python prioritise/gate.py reports/ranked.sarif [--force] [--config ...] \
      [--verdicts reports/verdicts.json]
  # exit 0 = pass, 1 = policy violated, 2 = usage error
"""
from __future__ import annotations
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402


def load_verdicts(path: str) -> dict:
    """content_hash -> verdict string, from a dispatcher verdicts.json (if any)."""
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    items = data.get("verdicts", data) if isinstance(data, dict) else data
    out = {}
    for v in items or []:
        if isinstance(v, dict) and v.get("content_hash"):
            out[v["content_hash"]] = str(v.get("verdict", "")).lower()
    return out


def is_violation(beacon: dict, gate: dict, confirmed: dict) -> bool:
    w = (beacon.get("properties") or {}).get(S.WP) or {}
    if w.get("suppressed"):
        return False
    fail_axes = set(gate.get("fail_on_axes") or [])
    axes = set(w.get("axes") or [])
    if fail_axes and not (axes & fail_axes):
        return False
    prior_hit = float(w.get("severity_prior", 0)) >= float(gate.get("min_severity_prior", 0.9))
    level_hit = beacon.get("level") in (gate.get("fail_on_levels") or [])
    if not (prior_hit or level_hit):
        return False
    if gate.get("only_confirmed"):
        return confirmed.get(w.get("content_hash")) == "confirm"
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fail the run when beacons violate policy.")
    ap.add_argument("ranked", help="ranked beacon SARIF (from rank.py)")
    ap.add_argument("--force", action="store_true", help="run even if gate.enabled is false")
    ap.add_argument("--config", default=None)
    ap.add_argument("--verdicts", default=None)
    a = ap.parse_args(argv)

    config = S.load_config(a.config)
    gate = config.get("gate", {}) or {}
    if not gate.get("enabled") and not a.force:
        print("gate: disabled (set gate.enabled: true or pass --force) — not gating")
        return 0

    root = S.repo_root()
    verdicts_path = a.verdicts or os.path.join(
        root, config.get("dispatch", {}).get("verdicts", "reports/verdicts.json"))
    confirmed = load_verdicts(verdicts_path)

    runs = (S.read_sarif(a.ranked).get("runs") or [{}])
    beacons = list((runs[0] or {}).get("results", []) or [])
    violations = [b for b in beacons if is_violation(b, gate, confirmed)]

    max_v = int(gate.get("max_violations", 0))
    fail = len(violations) > max_v

    print(f"gate: {len(violations)} violation(s) "
          f"(axes={gate.get('fail_on_axes') or 'any'}, "
          f"prior>={gate.get('min_severity_prior')}, levels={gate.get('fail_on_levels')}"
          f"{', confirmed-only' if gate.get('only_confirmed') else ''}); "
          f"threshold max_violations={max_v}")
    for b in sorted(violations, key=lambda x: S.get_wp(x, "score", 0), reverse=True)[:20]:
        w = b["properties"][S.WP]; loc = S.result_location(b)
        print(f"  [--] {loc['uri']}:{loc['start_line']}  [{','.join(w.get('axes', []))}] "
              f"score={w.get('score')} {b.get('ruleId')}")
    if fail:
        print(f"gate: FAIL — {len(violations)} violation(s) exceed max_violations={max_v}")
        return 1
    print("gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
