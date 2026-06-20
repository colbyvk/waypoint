#!/usr/bin/env python3
"""
incremental.py — combine a changed-files scan with a cached baseline.

`--changed` scans only the files that changed (seconds), so its beacon file
covers just those files. To still show the FULL picture, we splice in the cached
baseline beacons for every file that did NOT change:

    combined = fresh(changed files) + baseline(every file NOT in the changed set)

So the output is the complete beacon set, computed in seconds. Pure stdlib.

Usage:
  incremental.py fresh.sarif --baseline baseline.sarif --changed changed.txt \
      -o combined.sarif [--base REPO_ROOT]
"""
from __future__ import annotations
import argparse, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402


def _rel(uri: str, base: str) -> str:
    p = S._strip_uri(uri or "")
    if base and os.path.isabs(p):
        try:
            p = os.path.relpath(p, base)
        except ValueError:
            pass
    return p.replace("\\", "/")


def _results(path: str) -> list:
    if not path or not os.path.isfile(path):
        return []
    return list((S.read_sarif(path).get("runs") or [{}])[0].get("results") or [])


def combine(fresh: list, baseline: list, changed_files: list, base: str) -> list:
    """Fresh beacons for the changed files + baseline beacons for everything else.
    A baseline beacon is dropped if its file changed (the fresh scan re-covered it)
    or its file already appears in the fresh set."""
    changed = {_rel(c, base) for c in changed_files}
    fresh_files = {_rel(S.result_location(b).get("uri", ""), base) for b in fresh}
    out = list(fresh)
    for b in baseline:
        f = _rel(S.result_location(b).get("uri", ""), base)
        if f in changed or f in fresh_files:
            continue
        out.append(b)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Splice a changed-files scan into a cached baseline.")
    ap.add_argument("fresh", help="beacons from the changed-files scan")
    ap.add_argument("--baseline", required=True, help="cached full beacons from a prior scan")
    ap.add_argument("--changed", required=True, help="file listing the changed paths")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--base", default=S.repo_root())
    a = ap.parse_args(argv)

    fresh, baseline = _results(a.fresh), _results(a.baseline)
    changed_files = [ln.strip() for ln in open(a.changed, encoding="utf-8")
                     if ln.strip()] if os.path.isfile(a.changed) else []
    combined = combine(fresh, baseline, changed_files, a.base)

    out = S.empty_sarif("waypoint")
    out["runs"][0]["results"] = combined
    out["runs"][0]["properties"] = {"waypoint_stage": "incremental",
                                    "changed_files": len(changed_files)}
    S.write_sarif(out, a.out)
    print(f"incremental: {len(fresh)} fresh + {len(baseline)} baseline "
          f"-> {len(combined)} combined ({len(changed_files)} changed file(s)) -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
