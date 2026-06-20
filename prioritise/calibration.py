#!/usr/bin/env python3
"""
calibration.py — per-rule precision calibration (closes the recall→precision loop).

Waypoint's cheap pass is recall-tuned: it raises many beacons on purpose. Over
time the agent (or a human) confirms or dismisses them. This module turns that
history into a per-RULE precision estimate and a score multiplier, so rules that
keep getting dismissed sink in the ranking and rules that get confirmed rise —
the ranker learns which detectors actually point at real problems on YOUR repos.

Sources (read-only — never touches the agent layer):
  * reports/verdicts.json   — confirm/dismiss/escalate per beacon (carries rule_id)
  * suppression/store.json   — recorded dismissals (carry rule_id)

Neutral by construction: with no history every rule gets precision 0.5 -> factor
1.0, so ranking is unchanged until verdicts accumulate. Pure standard library.
"""
from __future__ import annotations
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402

CONFIRMED = {"confirm", "confirmed", "true_positive", "tp", "valid", "real"}
DISMISSED = {"dismiss", "dismissed", "false_positive", "fp", "invalid", "wontfix"}

DEFAULT_STORE = "suppression/calibration.json"


def _verdict_rule(v: dict) -> str | None:
    rid = v.get("rule_id")
    if rid:
        return rid
    dets = v.get("detectors") or []          # "tool:rule_id"
    if dets and isinstance(dets[0], str):
        return dets[0].split(":")[-1] or None
    return None


def gather_observations(root: str, config: dict) -> dict:
    """Return {rule_id: {'confirm': n, 'dismiss': n}} deduped by content_hash."""
    obs: dict[str, dict[str, int]] = {}
    seen: set[str] = set()

    def bump(rid, kind):
        if rid:
            obs.setdefault(rid, {"confirm": 0, "dismiss": 0})[kind] += 1

    vpath = os.path.join(root, config.get("dispatch", {}).get("verdicts", "reports/verdicts.json"))
    if os.path.isfile(vpath):
        try:
            data = json.load(open(vpath, encoding="utf-8"))
        except (OSError, ValueError):
            data = None
        verdicts = data.get("verdicts", data) if isinstance(data, dict) else data
        for v in verdicts or []:
            if not isinstance(v, dict):
                continue
            verd = str(v.get("verdict", "")).lower()
            h = v.get("content_hash")
            if h:
                seen.add(h)
            if verd in CONFIRMED:
                bump(_verdict_rule(v), "confirm")
            elif verd in DISMISSED:
                bump(_verdict_rule(v), "dismiss")

    spath = os.path.join(root, config.get("suppression", {}).get("store", "suppression/store.json"))
    if os.path.isfile(spath):
        try:
            store = json.load(open(spath, encoding="utf-8"))
        except (OSError, ValueError):
            store = {}
        for e in store.get("suppressions", []) or []:
            h = e.get("content_hash")
            if h in seen:                       # already counted from verdicts.json
                continue
            if str(e.get("verdict", "")).lower() in DISMISSED:
                bump(e.get("rule_id"), "dismiss")
                if h:
                    seen.add(h)
    return obs


def precision(confirm: int, dismiss: int, strength: float) -> float:
    """Laplace-smoothed precision. No data -> 0.5 (neutral)."""
    return (confirm + strength / 2.0) / (confirm + dismiss + strength)


def factor(p: float, min_f: float, max_f: float) -> float:
    """Map precision [0,1] -> multiplier, with p=0.5 pinned to 1.0 (neutral)."""
    if p >= 0.5:
        return round(1.0 + (p - 0.5) / 0.5 * (max_f - 1.0), 4)
    return round(1.0 - (0.5 - p) / 0.5 * (1.0 - min_f), 4)


def compute(obs: dict, ccfg: dict) -> dict:
    strength = float(ccfg.get("prior_strength", 4))
    min_f = float(ccfg.get("min_factor", 0.4))
    max_f = float(ccfg.get("max_factor", 1.3))
    rules = {}
    for rid, cd in obs.items():
        c, d = cd["confirm"], cd["dismiss"]
        p = precision(c, d, strength)
        rules[rid] = {"confirm": c, "dismiss": d, "n": c + d,
                      "precision": round(p, 4), "factor": factor(p, min_f, max_f)}
    return {"version": 1, "rules": rules}


def load(path: str) -> dict:
    if path and os.path.isfile(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            return {}
    return {}


def factor_for(rule_ids, calib: dict, ccfg: dict) -> float:
    """Score multiplier for a beacon: the MOST conservative (lowest) factor among
    its contributing rules that have calibration data; 1.0 if none / disabled."""
    if not calib or not ccfg.get("enabled", True):
        return 1.0
    rules = calib.get("rules", {})
    facs = [rules[r]["factor"] for r in (rule_ids or []) if r in rules]
    return min(facs) if facs else 1.0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Recompute per-rule precision calibration from verdict history.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--config", default=None)
    a = ap.parse_args(argv)
    root = S.repo_root()
    config = S.load_config(a.config)
    ccfg = config.get("scoring", {}).get("calibration", {})
    out = a.out or os.path.join(root, config.get("suppression", {}).get("calibration_store", DEFAULT_STORE))
    obs = gather_observations(root, config)
    calib = compute(obs, ccfg)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(calib, open(out, "w", encoding="utf-8"), indent=2)
    down = sum(1 for r in calib["rules"].values() if r["factor"] < 1.0)
    up = sum(1 for r in calib["rules"].values() if r["factor"] > 1.0)
    print(f"calibration: {len(calib['rules'])} rule(s) with verdict history "
          f"-> {down} down-weighted, {up} boosted -> {os.path.relpath(out, root)}")
    if not calib["rules"]:
        print("  (no verdict history yet — every rule stays neutral, factor 1.0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
