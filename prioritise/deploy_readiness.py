#!/usr/bin/env python3
"""
deploy_readiness.py — roll the ranked beacons + dark zone into a plain
"safe to ship?" readiness signal for the `deploy-check` skill to render.

This is a PRE-VERIFICATION suggestion only: it classifies what the scan FOUND by
the kind of deployment risk it usually represents. It never declares a repo safe
on its own — the agent (driven by the deploy-check skill) opens each ship-stopper,
confirms it, and renders the final verdict for the human. A beacon is a suspicion.

Buckets (by rule id / axis):
  ship-stopper — the things that actually get a vibe-coded app owned at deploy:
                 leaked secrets, unauthenticated endpoints, injection / RCE /
                 SSRF / deserialization, TLS-off, wildcard CORS, debug-on.
  review       — real but lower-impact: weak hash/cipher, insecure cookie/random,
                 open redirect, ReDoS, client-side secret exposure, …
  info         — everything else (logic / edge-case / style).

Usage:
  deploy_readiness.py reports/ranked.sarif [--blindspots reports/blindspots.json] [--base DIR]
"""
from __future__ import annotations
import argparse, json, os, re, sys

# Classification: rule id -> deployment-risk bucket. Bandit/Ruff numeric codes
# (S### == B###) are classed by number; our own rules + OSS-pack rules by
# substring. Ship-stopper wins over review; everything else is info.
_BANDIT_RX = re.compile(r"^[sb](\d{3})$", re.IGNORECASE)
BANDIT_SHIP = {"105", "106", "107",                                  # hardcoded secrets
               "201",                                                # flask debug=True
               "301", "302", "307", "308", "310",                   # pickle/marshal/eval/mark_safe/urlopen
               "313", "314", "315", "316", "317", "318", "319", "320",  # xml / XXE
               "323", "501", "502", "503", "504",                    # TLS off / bad ssl
               "506", "507",                                         # yaml.load / ssh no-hostkey
               "602", "604", "605", "608", "609", "610", "611"}      # shell / SQL / django raw
BANDIT_REVIEW = {"104", "108", "110", "112", "113",                  # bind-all / tmp / pass / no-timeout
                 "303", "304", "305", "306", "311", "312",           # weak crypto / mktemp / random
                 "321", "324", "601", "603", "606", "607"}

SHIP_STOPPER = (
    "secret", "hardcoded", "gitleaks", "trufflehog", "credential", "private-key",
    "authz", "no-auth", "route-no-auth", "privilege-from-request", "mass-assignment",
    "taint-", "sql", "eval-exec", "ts-eval", "command", "subprocess-shell",
    "os-popen", "deser", "pickle", "ssti", "xxe", "yaml-unsafe", "path-traversal",
    "fs-path-traversal", "ssrf", "dom-xss", "proto-pollution", "mark-safe",
    "flask-debug", "jwt-verify-disabled", "tls-verify-disabled", "cors-wildcard",
    "cdk-s3-public", "cdk-db-public", "cdk-sg-open-world", "cdk-iam-wildcard",
)
REVIEW = (
    "weak-hash", "weak-tls", "cipher-ecb", "insecure-random", "insecure-cookie",
    "csrf-exempt", "open-redirect", "redos", "dangerous-html", "unsafe-href",
    "target-blank", "token-in-webstorage", "process-env-in-client", "insecure-http",
    "postmessage", "request-no-timeout", "archive-extractall", "decompression",
    "tempfile", "toctou", "minidom", "ldap", "vm-runincontext", "child-process", "trivy",
)


def bucket(rid: str) -> str:
    r = (rid or "").lower()
    m = _BANDIT_RX.match(r)
    if m:
        n = m.group(1)
        return ("ship-stopper" if n in BANDIT_SHIP
                else "review" if n in BANDIT_REVIEW else "info")
    if any(k in r for k in SHIP_STOPPER):
        return "ship-stopper"
    if any(k in r for k in REVIEW):
        return "review"
    return "info"


def _signal(rid: str) -> str:
    r = (rid or "").lower()
    m = _BANDIT_RX.match(r)
    if m:
        n = m.group(1)
        if n in ("105", "106", "107"):
            return "secrets"
        if n in ("201", "323", "501", "502", "503", "504"):
            return "exposure"
        return "injection"
    if any(k in r for k in ("secret", "hardcoded", "credential", "gitleaks",
                            "trufflehog", "private-key")):
        return "secrets"
    if any(k in r for k in ("authz", "no-auth", "privilege", "mass-assignment")):
        return "auth"
    if any(k in r for k in ("cors", "tls-verify", "flask-debug", "public",
                            "open-world", "iam-wildcard")):
        return "exposure"
    return "injection"


def _wp(result: dict) -> dict:
    return (result.get("properties") or {}).get("waypoint") or {}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Deploy-readiness rollup for the deploy-check skill.")
    ap.add_argument("ranked", help="ranked beacon SARIF (from rank.py)")
    ap.add_argument("--blindspots", default=None, help="blindspots.json (dark zone)")
    ap.add_argument("--base", default=None, help="scanned dir (for display only)")
    ap.add_argument("--out", default=None, help="where to write deploy_readiness.json")
    a = ap.parse_args(argv)

    try:
        sarif = json.load(open(a.ranked, encoding="utf-8"))
        results = sarif["runs"][0]["results"]
    except (OSError, KeyError, IndexError, ValueError):
        results = []

    ship, review = [], []
    sig_counts = {"secrets": 0, "auth": 0, "injection": 0, "exposure": 0}
    for r in results:
        wp = _wp(r)
        rid = wp.get("rule_id") or r.get("ruleId") or ""
        b = bucket(rid)
        if b == "info":
            continue
        try:
            loc = r["locations"][0]["physicalLocation"]
            where = f'{loc["artifactLocation"]["uri"]}:{loc["region"]["startLine"]}'
        except (KeyError, IndexError, TypeError):
            where = "?"
        item = {"rule": rid, "where": where, "rank": wp.get("rank"),
                "axes": wp.get("axes", []), "level": r.get("level"),
                "boundary_reachable": wp.get("boundary_reachable"),
                "test_path": bool(wp.get("test_path")),
                "noncore_path": bool(wp.get("noncore_path"))}
        if b == "ship-stopper":
            ship.append(item); sig_counts[_signal(rid)] += 1
        else:
            review.append(item)

    # dark zone near danger — spots the scan could NOT verify, next to a sink
    dark = {"code_exec": 0, "sink": 0}
    if a.blindspots and os.path.exists(a.blindspots):
        try:
            bs = json.load(open(a.blindspots, encoding="utf-8"))
            tiers = (bs.get("summary") or {}).get("tiers") or {}
            dark["code_exec"] = int(tiers.get("code-exec-adjacent", 0))
            dark["sink"] = int(tiers.get("sink-adjacent", 0))
        except (OSError, ValueError, TypeError):
            pass

    if ship:
        level = "RED"
    elif review or dark["code_exec"] or dark["sink"]:
        level = "YELLOW"
    else:
        level = "GREEN"

    out = {
        "suggested_level": level,
        "pre_verification": True,
        "ship_stoppers": ship,
        "review": review,
        "dark_near_danger": dark,
        "counts": {"ship_stoppers": len(ship), "review": len(review),
                   "by_signal": sig_counts},
    }
    out_path = a.out or os.path.join(os.path.dirname(os.path.abspath(a.ranked)),
                                     "deploy_readiness.json")
    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
    except OSError:
        pass

    brk = " · ".join(f"{k} {v}" for k, v in sig_counts.items() if v)
    print(f"deploy readiness (PRE-verification — the agent confirms before declaring):")
    print(f"  suggested: {level}")
    print(f"  ship-stoppers: {len(ship)}" + (f"   ({brk})" if brk else ""))
    print(f"  review: {len(review)}")
    print(f"  dark zone near danger: {dark['code_exec']} code-exec-adjacent, "
          f"{dark['sink']} sink-adjacent (verify by hand)")
    print(f"  -> {os.path.relpath(out_path)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
