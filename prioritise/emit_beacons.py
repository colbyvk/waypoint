#!/usr/bin/env python3
"""
emit_beacons.py — drop the beacons as Markdown.

Waypoint is NOT a linter: it does not emit diagnostics for a human to wade
through — it DROPS BEACONS, markers on regions worth attention. This stage
writes those beacons as Markdown so they are the human-facing artifact:

  reports/beacons/<rank>_<hash>.md   one file per beacon — file path + the
                                     classification of the issue + why
  reports/BEACONS.md                 the index of every beacon (path + class)

Reads the ranked beacons (reports/ranked.sarif). Deterministic; no AI.
"""
from __future__ import annotations
import argparse, datetime, glob, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402


def classification(w: dict) -> str:
    cls = ", ".join(w.get("axes", []) or []) or "unclassified"
    subt = w.get("subtags", []) or []
    return cls + (f" — {', '.join(subt)}" if subt else "")


def detectors_of(w: dict) -> str:
    tools = sorted({m.get("tool") for m in w.get("merged_from", []) if m.get("tool")})
    return ", ".join(tools) or (w.get("tool") or "?")


def emit(ranked_path: str, out_dir: str, index_path: str, cap: int | None = None) -> tuple[int, int]:
    runs = S.read_sarif(ranked_path).get("runs") or [{}]
    beacons_all = list((runs[0] or {}).get("results", []) or [])
    total = len(beacons_all)

    # rank.py already orders by score; sort defensively, then keep only the top-N
    # for the HUMAN-facing artifacts (one .md per beacon + the INDEX table). A
    # 360-row INDEX is unreadable; the FULL ranked set always stays in
    # reports/ranked.sarif for tooling / the agent. cap=None means "emit all".
    def _score(b):
        w = (b.get("properties") or {}).get(S.WP, {})
        return (-(w.get("score") or 0.0), w.get("rank") or 10 ** 9)
    beacons_all.sort(key=_score)
    beacons = beacons_all[:cap] if cap else beacons_all

    os.makedirs(out_dir, exist_ok=True)
    for stale in glob.glob(os.path.join(out_dir, "*.md")):   # clear last run's beacons
        os.remove(stale)

    rows = []
    for b in beacons:
        w = (b.get("properties") or {}).get(S.WP, {})
        loc = S.result_location(b)
        rank = w.get("rank") or 0
        chash = w.get("content_hash") or "nohash"
        rule = w.get("rule_id") or b.get("ruleId") or "?"
        cls = classification(w)
        span = ""
        if loc.get("end_line") and loc["end_line"] != loc.get("start_line"):
            span = f" (lines {loc['start_line']}–{loc['end_line']})"
        stem = f"{rank:04d}_{chash[:10]}"
        body = [
            f"# Beacon #{rank} — {', '.join(w.get('axes', [])) or 'unclassified'}",
            "",
            f"- **File:** `{loc.get('uri')}:{loc.get('start_line')}`{span}",
            f"- **Classification:** {cls}",
            f"- **Rule:** `{rule}`",
            f"- **Raised by:** {detectors_of(w)}",
            f"- **Severity prior:** {w.get('severity_prior')}  ·  "
            f"**Score:** {w.get('score')}  ·  **Boundary-reachable:** {w.get('boundary_reachable')}",
            f"- **Content hash:** `{chash}`",
            "",
            f"> **Why this region was beaconed:** {S.redact_secrets(w.get('hypothesis') or S.result_message(b))}",
            "",
        ]
        # Dynamic-evidence beacons (property/fuzz lane) carry the violated
        # property and the minimal input that reproduces the failure — the
        # difference between "look here" and "run this and watch it break".
        # All free text is run through redact_secrets so a secrets finding can
        # never write the secret itself into the beacon.
        if w.get("property"):
            body += [f"> **Property violated:** {S.redact_secrets(w['property'])}", ""]
        if w.get("reproducing_input"):
            body += [f"> **Reproducing input:** `{S.redact_secrets(w['reproducing_input'])}`", ""]
        with open(os.path.join(out_dir, stem + ".md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(body))
        rows.append((rank, f"`{loc.get('uri')}:{loc.get('start_line')}`", cls, rule,
                     w.get("score"), stem + ".md"))

    rows.sort(key=lambda r: (-(r[4] or 0), r[0]))
    idx_dir = os.path.dirname(os.path.abspath(index_path))
    today = datetime.date.today().isoformat()
    shown = len(beacons)
    capped = cap is not None and total > shown
    idx = [
        (f"# Beacons — showing top {shown} of {total} ({today})" if capped
         else f"# Beacons — {total} dropped ({today})"),
        "",
        "Waypoint **drops beacons** — markers on regions worth review, each with its "
        "**file path** and the **classification** of the issue. This is not a linter "
        "report: every beacon is a handoff to an agent or a reviewer, never a raw "
        "diagnostic to triage by hand.",
        "",
    ]
    if capped:
        idx += [f"> Showing the **{shown} highest-scored** beacons. The full ranked set "
                f"(all **{total}**) is in `reports/ranked.sarif`; raise the cap with "
                f"`emit.top_n` in `waypoint.config.yaml`.", ""]
    idx += [
        "> [!] **Sensitivity:** beacons may quote matched code; detected secrets are "
        "redacted here, but the raw tool output under `reports/` is **not** — do not "
        "commit or publicly share it.",
        "",
        "| # | File | Classification | Rule | Score |",
        "|---|------|----------------|------|-------|",
    ]
    for rank, fileref, cls, rule, score, md in rows:
        link = os.path.relpath(os.path.join(out_dir, md), idx_dir)
        idx.append(f"| [{rank}]({link}) | {fileref} | {cls} | `{rule}` | {score} |")
    idx.append("")
    os.makedirs(os.path.dirname(os.path.abspath(index_path)), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(idx))
    return len(beacons), total


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit beacons as Markdown (file path + classification).")
    ap.add_argument("ranked", nargs="?", default=None, help="ranked beacon SARIF")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--index", default=None)
    ap.add_argument("--top-n", type=int, default=None,
                    help="max beacons in the human INDEX/.md (full set stays in ranked.sarif)")
    a = ap.parse_args(argv)
    root = S.repo_root()
    config = S.load_config(None)
    cap = a.top_n if a.top_n is not None else int((config.get("emit") or {}).get("top_n", 40))
    cap = cap if cap > 0 else None
    ranked = a.ranked or os.path.join(root, "reports", "ranked.sarif")
    out_dir = a.out_dir or os.path.join(root, "beacons")
    index = a.index or os.path.join(root, "beacons", "INDEX.md")
    shown, total = emit(ranked, out_dir, index, cap=cap)
    extra = f" (top {shown} of {total})" if total > shown else ""
    print(f"emit_beacons: dropped {shown} beacon .md files{extra} -> {os.path.relpath(out_dir, root)}/ "
          f"(+ {os.path.relpath(index, root)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
