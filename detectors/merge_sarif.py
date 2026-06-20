#!/usr/bin/env python3
"""
merge_sarif.py  —  Phase 1 core (spec §10, §13).

Merge every per-tool SARIF file into ONE beacon file:
  * normalize each result into a Waypoint beacon (axes, severity prior,
    hypothesis, content hash) using rule metadata or tag_map.yaml,
  * dedup overlapping regions into a single MULTI-TAGGED beacon (spec §9 dedup),
  * write a well-formed SARIF 2.1.0 log to the output path.

This stage has NO AI in it and is fully deterministic. The raw per-tool SARIF
inputs are left untouched on disk — they are the auditable "what fired" record
(spec §2.3); this file is the deduplicated view used downstream.

Usage:
  python detectors/merge_sarif.py reports/*.sarif -o reports/beacons.sarif \
      [--base REPO_ROOT] [--config waypoint.config.yaml]
"""

from __future__ import annotations

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # find sariflib
import sariflib as S  # noqa: E402

_LEVEL_RANK = {"none": 0, "note": 1, "warning": 2, "error": 3}


# --------------------------------------------------------------------------- #
# tag resolution: a beacon's axes + agent hypothesis
# --------------------------------------------------------------------------- #
def _fill(template: str, ctx: dict) -> str:
    out = template or ""
    for key, val in ctx.items():
        out = out.replace("{" + key + "}", str(val))
    return out


def resolve_axes_and_hypothesis(run, result, tool, tag_map, base):
    """Return (axes, subtags, hypothesis).

    Precedence:
      1. Our own Semgrep rules carry waypoint_axes / waypoint_hypothesis in rule
         metadata (or result.properties) — trust them verbatim.
      2. Otherwise apply tag_map.yaml: tool block -> first matching rule -> axes.
      3. Otherwise the global default (single 'edge-case' axis).
    """
    rid = S.result_rule_id(result)
    sym = S.result_symbol(result) or S.enclosing_symbol(base, S.result_location(result))
    loc = S.result_location(result)
    ctx = {
        "symbol": sym or "this region",
        "file": loc.get("uri") or "?",
        "line": loc.get("start_line") or "?",
        "rule": rid,
        "message": S.result_message(result),
    }

    # (1) native waypoint metadata (our custom rules)
    meta = S.result_rule_metadata(run, result)
    props = result.get("properties")
    props = props if isinstance(props, dict) else {}    # tolerate malformed SARIF
    axes = meta.get("waypoint_axes") or props.get("waypoint_axes")
    if axes:
        hyp = (meta.get("waypoint_hypothesis") or props.get("waypoint_hypothesis")
               or ctx["message"] or "Confirm or deny this finding.")
        subtags = meta.get("waypoint_subtags") or props.get("waypoint_subtags") or []
        return _split_axes(axes, subtags) + (_fill(hyp, ctx),)

    # (2) tag_map
    tools = (tag_map.get("tools") or {})
    block = tools.get(tool) or tools.get(tool.lower())
    if block:
        for entry in block.get("rules") or []:
            if S.imatch(rid, entry.get("match", "")):
                a, st = _split_axes(entry.get("axes") or ["edge-case"], entry.get("subtags") or [])
                return a, st, _fill(entry.get("hypothesis", ""), ctx)
        dflt = block.get("_default") or {}
        a, st = _split_axes(dflt.get("axes") or ["edge-case"], dflt.get("subtags") or [])
        return a, st, _fill(dflt.get("hypothesis") or ctx["message"], ctx)

    # (3) global default
    gd = tag_map.get("_global_default") or {"axes": ["edge-case"], "hypothesis": ctx["message"]}
    a, st = _split_axes(gd.get("axes") or ["edge-case"], gd.get("subtags") or [])
    return a, st, _fill(gd.get("hypothesis", ""), ctx)


def _split_axes(axes, subtags):
    """Separate the four canonical axes from any free-form sub-tags."""
    axes = [a for a in (axes or []) if a]
    primary = [a for a in axes if a in S.AXES]
    extra = [a for a in axes if a not in S.AXES]
    if not primary:                      # never leave a beacon axis-less
        primary = ["edge-case"]
    subtags = sorted(set(list(subtags or []) + extra))
    return sorted(set(primary)), subtags


# --------------------------------------------------------------------------- #
# normalize one raw result into a beacon
# --------------------------------------------------------------------------- #
def _relativize(result, base):
    """Rewrite absolute file URIs under `base` to repo-relative form, so content
    hashes, allowlist globs and agent prompts are stable across machines/CI."""
    base = os.path.abspath(base)
    for loc in result.get("locations", []) or []:
        art = ((loc.get("physicalLocation") or {}).get("artifactLocation")) or {}
        uri = art.get("uri")
        if not uri:
            continue
        u = S._strip_uri(uri)
        ab = os.path.abspath(u if os.path.isabs(u) else os.path.join(base, u))
        art["uri"] = os.path.relpath(ab, base) if ab.startswith(base + os.sep) else u


def normalize_one(run, result, config, tag_map, base):
    _relativize(result, base)   # make paths repo-relative before hashing
    tool = S.tool_name(run)
    axes, subtags, hypothesis = resolve_axes_and_hypothesis(run, result, tool, tag_map, base)
    level = S.result_level(result, run)
    prior = S.severity_prior(result, run, config)
    chash = S.content_hash(base, result)
    rid = S.result_rule_id(result)
    msg = S.result_message(result)
    loc = result.get("locations") or _synth_locations(result)

    beacon = {
        "ruleId": rid,
        "level": level,
        "message": {"text": msg},
        "locations": loc,
        "properties": {
            S.WP: {
                "axes": axes,
                "subtags": subtags,
                "severity_prior": round(prior, 4),
                "hypothesis": hypothesis,
                "content_hash": chash,
                "tool": tool,
                "rule_id": rid,
                "merged_from": [{"tool": tool, "rule_id": rid, "level": level, "message": msg}],
            }
        },
    }
    # carry CVSS through if present (lets the Security tab rank dependency CVEs)
    rprops = result.get("properties")
    sec = rprops.get("security-severity") if isinstance(rprops, dict) else None
    if sec is not None:
        beacon["properties"]["security-severity"] = sec
    # carry dynamic-evidence fields: the logic lane (property/fuzz) attaches the
    # minimal reproducing input and the violated property to the result props.
    # These turn a beacon from "this region looks suspect" into "this input
    # breaks it" — the actionability that static beacons can't carry.
    if isinstance(rprops, dict):
        for src_key, dst_key in (("waypoint_reproducing_input", "reproducing_input"),
                                 ("waypoint_property", "property")):
            val = rprops.get(src_key)
            if val:
                beacon["properties"][S.WP][dst_key] = val
    return beacon


def _synth_locations(result):
    """Build a minimal locations array if the tool omitted one."""
    loc = S.result_location(result)
    if not loc.get("uri"):
        return []
    region = {"startLine": max(1, loc.get("start_line") or 1)}
    if loc.get("end_line"):
        region["endLine"] = loc["end_line"]
    return [{"physicalLocation": {
        "artifactLocation": {"uri": loc["uri"]},
        "region": region,
    }}]


# --------------------------------------------------------------------------- #
# dedup: merge overlapping regions into one multi-tagged beacon (spec §9)
# --------------------------------------------------------------------------- #
def _beacon_loc(beacon):
    return S.result_location(beacon)


def _merge_cluster(cluster, base):
    """Fold a cluster of overlapping beacons into one multi-tagged beacon."""
    if len(cluster) == 1:
        return cluster[0]
    # strongest beacon (by prior, then level) supplies the headline hypothesis
    cluster = sorted(
        cluster,
        key=lambda b: (S.get_wp(b, "severity_prior", 0), _LEVEL_RANK.get(b.get("level"), 0)),
        reverse=True,
    )
    head = cluster[0]
    axes, subtags, merged_from = set(), set(), []
    max_prior, best_level = 0.0, "none"
    repro, prop = None, None
    starts, ends, uri = [], [], _beacon_loc(head).get("uri")
    for b in cluster:
        w = b.get("properties", {}).get(S.WP, {})
        axes.update(w.get("axes") or [])
        subtags.update(w.get("subtags") or [])
        merged_from.extend(w.get("merged_from") or [])
        repro = repro or w.get("reproducing_input")   # keep the first concrete
        prop = prop or w.get("property")               # repro/property in the cluster
        max_prior = max(max_prior, w.get("severity_prior", 0))
        if _LEVEL_RANK.get(b.get("level"), 0) > _LEVEL_RANK.get(best_level, 0):
            best_level = b.get("level")
        loc = _beacon_loc(b)
        if loc.get("start_line"):
            starts.append(loc["start_line"])
            ends.append(loc["end_line"] or loc["start_line"])

    # widest enclosing region -> canonical location + stable content hash
    merged_loc = dict(head.get("locations", [{}])[0]) if head.get("locations") else {}
    if starts:
        s, e = min(starts), max(ends)
        merged_loc = {"physicalLocation": {
            "artifactLocation": {"uri": uri},
            "region": {"startLine": s, "endLine": e},
        }}
        # preserve a logical location if the head had one
        if head.get("locations") and head["locations"][0].get("logicalLocations"):
            merged_loc["logicalLocations"] = head["locations"][0]["logicalLocations"]
    # Identify the merged beacon by the HEAD (strongest) member's OWN region hash,
    # never the widened union span. If we hashed the union, the hash would shift
    # whenever a nearby detector starts/stops firing, re-raising an already
    # dismissed beacon — the §9 suppression guarantee must survive merge-partner
    # churn, so it keys off the most stable member (the highest-severity one).
    chash = S.get_wp(head, "content_hash")

    wp = {
        "axes": sorted(axes),
        "subtags": sorted(subtags),
        "severity_prior": round(max_prior, 4),
        "hypothesis": S.get_wp(head, "hypothesis"),
        "content_hash": chash,
        "tool": "waypoint-merged",
        "rule_id": S.get_wp(head, "rule_id"),
        "merged_from": merged_from,
    }
    if repro:
        wp["reproducing_input"] = repro
    if prop:
        wp["property"] = prop
    return {
        "ruleId": S.get_wp(head, "rule_id"),
        "level": best_level,
        "message": {"text": S.result_message(head)},
        "locations": [merged_loc] if merged_loc else head.get("locations", []),
        "properties": {S.WP: wp},
    }


def dedup(beacons, base):
    """Merge beacons covering the same region. Returns merged list + stats."""
    located, unlocated = {}, {}
    for b in beacons:
        loc = _beacon_loc(b)
        # source regions merge by line overlap; dependency-manifest findings and
        # region-less findings dedup by content hash (distinct advisories stay
        # distinct, identical re-reports collapse).
        if loc.get("start_line") and not S.is_manifest(loc.get("uri", "")):
            located.setdefault(loc["uri"], []).append(b)
        else:
            unlocated.setdefault(S.get_wp(b, "content_hash"), []).append(b)

    merged = []
    # interval-merge the located beacons per file
    for uri, items in located.items():
        items.sort(key=lambda b: (_beacon_loc(b)["start_line"], _beacon_loc(b)["end_line"]))
        cluster, cur_end = [], None
        for b in items:
            loc = _beacon_loc(b)
            if cluster and loc["start_line"] <= cur_end:
                cluster.append(b)
                cur_end = max(cur_end, loc["end_line"])
            else:
                if cluster:
                    merged.append(_merge_cluster(cluster, base))
                cluster, cur_end = [b], loc["end_line"]
        if cluster:
            merged.append(_merge_cluster(cluster, base))
    # merge identical unlocated beacons
    for _, items in unlocated.items():
        merged.append(_merge_cluster(items, base))

    n_multi = sum(1 for b in merged if len(S.get_wp(b, "axes", [])) > 1)
    stats = {"in": len(beacons), "out": len(merged), "multi_axis": n_multi}
    return merged, stats


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def build_driver_rules(beacons):
    """Minimal driver.rules so the SARIF renders natively (one entry per id)."""
    seen, rules = {}, []
    for b in beacons:
        rid = b.get("ruleId") or "unknown"
        if rid in seen:
            continue
        seen[rid] = True
        w = b.get("properties", {}).get(S.WP, {})
        rules.append({
            "id": rid,
            "name": rid,
            "shortDescription": {"text": (S.result_message(b) or rid)[:120]},
            "properties": {"waypoint_axes": w.get("axes", [])},
        })
    return rules


def main(argv=None):
    ap = argparse.ArgumentParser(description="Merge per-tool SARIF into one beacon file.")
    ap.add_argument("inputs", nargs="+", help="input SARIF files or globs")
    ap.add_argument("-o", "--out", required=True, help="output beacon SARIF path")
    ap.add_argument("--base", default=S.repo_root(), help="repo root for resolving file regions")
    ap.add_argument("--config", default=None, help="waypoint.config.yaml path")
    args = ap.parse_args(argv)

    config = S.load_config(args.config)
    tag_map_path = os.path.join(S.repo_root(), config.get("tag_map", "tag_map.yaml"))
    tag_map = S.load_yaml(tag_map_path) if os.path.exists(tag_map_path) else {}

    # expand globs (shells usually do this, but be robust when they don't)
    paths = []
    for pat in args.inputs:
        hits = glob.glob(pat)
        paths.extend(hits if hits else ([pat] if os.path.exists(pat) else []))
    paths = sorted(set(paths))
    if not paths:
        print("merge_sarif: no input SARIF files matched", file=sys.stderr)
        # still emit a valid empty beacon file so downstream stages don't crash
        S.write_sarif(S.empty_sarif("waypoint"), args.out)
        return 0

    raw_beacons = []
    per_tool = {}
    for path in paths:
        try:
            sarif = S.read_sarif(path)
        except (OSError, ValueError) as exc:
            print(f"merge_sarif: skipping unreadable {path}: {exc}", file=sys.stderr)
            continue
        for run, result in S.iter_results(sarif):
            # Never re-ingest our own stage outputs (beacons/ranked/suppressed) —
            # the CI glob `reports/*.sarif` would otherwise feed merge on itself.
            if S.tool_name(run).startswith("waypoint"):
                continue
            raw_beacons.append(normalize_one(run, result, config, tag_map, args.base))
            t = S.tool_name(run)
            per_tool[t] = per_tool.get(t, 0) + 1

    merged, stats = dedup(raw_beacons, args.base)
    merged.sort(key=lambda b: (_beacon_loc(b).get("uri", ""), _beacon_loc(b).get("start_line", 0)))

    out = S.empty_sarif("waypoint", rules=build_driver_rules(merged))
    out["runs"][0]["results"] = merged
    out["runs"][0]["properties"] = {"waypoint_stage": "merged",
                                    "source_tools": sorted(per_tool)}

    errs = S.validate_sarif(out)
    if errs:
        print("merge_sarif: WARNING output failed structural validation:", file=sys.stderr)
        for e in errs[:10]:
            print("   -", e, file=sys.stderr)

    S.write_sarif(out, args.out)

    # axis tally for the run log
    axis_tally = {a: 0 for a in S.AXES}
    for b in merged:
        for a in S.get_wp(b, "axes", []):
            axis_tally[a] = axis_tally.get(a, 0) + 1
    print(f"merge_sarif: {stats['in']} raw -> {stats['out']} beacons "
          f"({stats['multi_axis']} multi-axis) from {len(per_tool)} tool(s)")
    print("  by tool:  " + ", ".join(f"{t}={n}" for t, n in sorted(per_tool.items())))
    print("  by axis:  " + ", ".join(f"{a}={axis_tally[a]}" for a in S.AXES))
    print(f"  -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
