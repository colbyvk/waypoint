#!/usr/bin/env python3
"""
fallback_dispatcher.py — OPTIONAL headless verification (spec §8).

Waypoint is a tool, not an agent: normally the agent (or human) that RUNS Waypoint
reads the beacons and verifies them — no model is called here, and no API key is
needed. This module exists only for UNATTENDED runs with no agent present.

It takes the top-N ranked beacons, assembles each one's CONTEXT ENVELOPE (the region
plus its immediate callers/callees — built here at dispatch time, not at detection
time, per §2.1), and turns each into a VERIFIER-shaped prompt: "here is a hypothesis,
here is the code, prove or disprove" — never an explorer prompt like "find bugs in
this repo".

Backends (waypoint.config.yaml dispatch.backend, or --backend):
  dry-run        write prompts to reports/dispatch/ and call NO model (DEFAULT —
                 deterministic, CI-safe, no key, costs nothing)
  claude-cli     shell out to the `claude` CLI in headless mode (`claude -p`)
  anthropic-api  call the Anthropic API (the ONLY backend that needs ANTHROPIC_API_KEY)
Verdicts (confirm/dismiss/escalate) are written to reports/verdicts.json — a
SEPARATE record from "what fired" (§2.3) — and dismissals are written back into
the suppression store so they do not re-raise.

Usage:
  python dispatch/fallback_dispatcher.py reports/ranked.sarif \
      [--backend dry-run] [--top-n 25] [--config waypoint.config.yaml]
  # close the loop from an externally-produced verdicts file:
  python dispatch/fallback_dispatcher.py --record reports/verdicts.json
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, subprocess, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "detectors"))
import sariflib as S  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prioritise"))
import suppress  # noqa: E402

_LANG = {".py": "python", ".rs": "rust", ".ts": "typescript", ".tsx": "tsx",
         ".js": "javascript", ".jsx": "jsx"}

SYSTEM_PROMPT = (
    "You are a precise code verifier. You are given ONE hypothesis about ONE "
    "region of code plus its surrounding context. CONFIRM, DISMISS, or ESCALATE "
    "the hypothesis using only the evidence shown plus sound reasoning. Do not "
    "hunt for unrelated issues. Reply with a SINGLE JSON object and nothing else:\n"
    '{"verdict":"confirm|dismiss|escalate","confidence":0.0-1.0,'
    '"evidence":["file:line ..."],"reasoning":"...","suggested_fix":"..."}'
)


# --------------------------------------------------------------------------- #
# context envelope
# --------------------------------------------------------------------------- #
def _read_lines(base: str, uri: str) -> list[str]:
    path = S.resolve_path(uri, base)
    if not path or not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def callees_in(region: str) -> list[str]:
    """Symbols invoked inside the region (immediate callees)."""
    found = re.findall(r"\b([A-Za-z_]\w*)\s*\(", region)
    skip = {"if", "for", "while", "switch", "catch", "return", "print", "len",
            "str", "int", "list", "dict", "set", "range", "super"}
    out = []
    for f in found:
        if f not in skip and f not in out:
            out.append(f)
    return out[:12]


def callers_of(symbol: str | None, base: str, exclude_dirs=("node_modules", "target", ".venv", ".git")) -> list[str]:
    """Sites across the repo that call the region's enclosing symbol."""
    if not symbol:
        return []
    pat = re.compile(r"\b" + re.escape(symbol) + r"\s*\(")
    hits = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fn in files:
            if not fn.endswith((".py", ".rs", ".ts", ".tsx", ".js", ".jsx")):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        if pat.search(line) and not re.match(
                                r"\s*(def|fn|function|async\s+def|pub\s+fn)\b", line):
                            hits.append(f"{os.path.relpath(path, base)}:{i}")
            except OSError:
                continue
    return hits[:10]


def build_envelope(beacon: dict, base: str, pad: int) -> dict:
    w = beacon["properties"][S.WP]
    loc = S.result_location(beacon)
    uri = loc.get("uri", "")
    lines = _read_lines(base, uri)
    start, end = loc.get("start_line", 1), loc.get("end_line", 1)
    sym = S.result_symbol(beacon) or S.enclosing_symbol(base, loc)
    lo, hi = max(1, start - pad), min(len(lines) or end, end + pad)
    region_pad = "\n".join(f"{i:>5} | {lines[i-1]}" for i in range(lo, hi + 1)) if lines else "(source unavailable)"
    region_only = "\n".join(lines[start-1:end]) if lines else ""
    return {
        "uri": uri, "start": start, "end": end, "symbol": sym,
        "axes": w.get("axes", []), "subtags": w.get("subtags", []),
        "severity_prior": w.get("severity_prior"), "rank": w.get("rank"),
        "score": w.get("score"), "content_hash": w.get("content_hash"),
        "hypothesis": w.get("hypothesis", ""),
        "detectors": [f'{m.get("tool")}:{m.get("rule_id")}' for m in w.get("merged_from", [])],
        "region_padded": region_pad, "callees": callees_in(region_only),
        "callers": callers_of(sym, base),
        "lang": _LANG.get(os.path.splitext(uri)[1].lower(), ""),
    }


def render_prompt(env: dict) -> str:
    callers = "\n".join(f"  - {c}" for c in env["callers"]) or "  (none found)"
    callees = ", ".join(env["callees"]) or "(none)"
    return f"""## Hypothesis (confirm or deny)
{env['hypothesis']}

## Beacon
file: {env['uri']}:{env['start']}-{env['end']}
enclosing symbol: {env['symbol'] or '(module scope)'}
axes: {', '.join(env['axes'])}{('  sub-tags: ' + ', '.join(env['subtags'])) if env['subtags'] else ''}
severity prior: {env['severity_prior']}   rank: {env['rank']}   score: {env['score']}
detectors that fired here: {', '.join(env['detectors'])}

## Region (with a few lines of context)
```{env['lang']}
{env['region_padded']}
```

## Immediate callees (symbols invoked in this region)
{callees}

## Callers of `{env['symbol']}` (paths that reach this region)
{callers}

## Your task
Decide confirm / dismiss / escalate for the hypothesis above, citing concrete
lines as evidence. Reply with the single JSON object described in the system
message.
"""


# --------------------------------------------------------------------------- #
# blind-spot (dark-zone) envelopes — coverage.py gaps, not beacons
# --------------------------------------------------------------------------- #
def build_gap_envelope(gap: dict, base: str, pad: int) -> dict:
    uri = gap.get("file", "")
    line = int(gap.get("line", 1) or 1)
    lines = _read_lines(base, uri)
    sym = gap.get("name") or gap.get("enclosing") or ""
    lo = max(1, line - pad)
    hi = min(len(lines) or line, line + 2 * pad)
    region_pad = ("\n".join(f"{i:>5} | {lines[i-1]}" for i in range(lo, hi + 1))
                  if lines else "(source unavailable)")
    region_only = "\n".join(lines[line-1:hi]) if lines else ""
    ch = hashlib.sha256(
        f"{uri}:{line}:{gap.get('kind')}:{sym}".encode()).hexdigest()[:24]
    return {
        "uri": uri, "line": line, "symbol": sym, "kind": gap.get("kind"),
        "hypothesis": gap.get("hypothesis", ""), "reasons": gap.get("reasons", []),
        "sinks": (gap.get("observed") or {}).get("sinks", []), "tier": gap.get("tier"),
        "content_hash": ch, "region_padded": region_pad,
        "callees": callees_in(region_only), "callers": callers_of(sym, base),
        "lang": _LANG.get(os.path.splitext(uri)[1].lower(), ""),
    }


def render_gap_prompt(env: dict) -> str:
    callers = "\n".join(f"  - {c}" for c in env["callers"]) or \
        "  (NONE found statically — reached only dynamically, or dead)"
    reasons = "\n".join(f"  - {r}" for r in env["reasons"]) or "  (unspecified)"
    sinks = ", ".join(env["sinks"]) or "(none detected)"
    return f"""## Blind spot to investigate — the static pass could NOT verify this region
{env['hypothesis']}

## Why this region is "dark"
kind: {env['kind']}   tier: {env.get('tier')}   reachability: UNRESOLVED
{reasons}
observed sinks in the parsed body: {sinks}

## Location
file: {env['uri']}:{env['line']}
symbol: {env['symbol'] or '(module scope)'}

## Region (with surrounding context)
```{env['lang']}
{env['region_padded']}
```

## Immediate callees (symbols invoked here)
{', '.join(env['callees']) or '(none)'}

## Static callers of `{env['symbol']}`
{callers}

## Your task
This code could not be verified by static analysis. Determine: (1) HOW it is
reached at runtime (framework route, hook/registration, reflection, event,
external caller); (2) whether attacker-controlled input can reach it; (3) whether
that creates a real vulnerability through the operations shown. If you cannot
establish a reachable path, DISMISS and say why. Reply with the single JSON
object described in the system message.
"""


# Tiers backed by OBSERVED facts (mirrors coverage.SHOWN_TIERS). opaque/unparsed
# regions are never auto-sent — we don't spend the LLM on what we didn't traverse.
_SHOWN_TIERS = ("code-exec-adjacent", "sink-adjacent")


def investigate(blindspots_path, base, backend, top_k, pad, model, out_dir,
                verdicts_path, store_path, expiry_days, root, min_rel=None):
    """Send the top-K OBSERVED-adjacent blind spots (code-exec / sink tiers) to the
    verifier — the LLM dark zone. opaque/unparsed regions are not auto-sent."""
    try:
        report = json.load(open(blindspots_path, encoding="utf-8"))
    except (OSError, ValueError):
        print(f"investigate: no readable blindspots at {blindspots_path} "
              f"(run a scan first)"); return 1
    gaps = [g for g in report.get("gaps", []) if g.get("tier") in _SHOWN_TIERS][:top_k]
    print(f"investigate: backend={backend}  budget=top {top_k}  blind spots={len(gaps)}")
    os.makedirs(out_dir, exist_ok=True)
    for stale in glob.glob(os.path.join(out_dir, "gap_*.md")):
        os.remove(stale)
    manifest, verdicts = [], []
    for i, gap in enumerate(gaps, 1):
        env = build_gap_envelope(gap, base, pad)
        prompt = render_gap_prompt(env)
        stem = f"gap_{i:03d}_{env['content_hash'][:10]}"
        with open(os.path.join(out_dir, stem + ".md"), "w", encoding="utf-8") as fh:
            fh.write(f"<!-- SYSTEM -->\n{SYSTEM_PROMPT}\n\n<!-- USER -->\n{prompt}")
        manifest.append({"rank": i, "file": env["uri"], "line": env["line"],
                         "kind": env["kind"], "content_hash": env["content_hash"],
                         "hypothesis": env["hypothesis"], "prompt_file": stem + ".md"})
        if backend == "dry-run":
            continue
        try:
            if backend == "claude-cli":
                verdict = call_claude_cli(SYSTEM_PROMPT, prompt, model)
            elif backend == "anthropic-api":
                verdict = call_anthropic_api(SYSTEM_PROMPT, prompt, model)
            else:
                raise SystemExit(f"unknown backend: {backend}")
        except Exception as exc:
            verdict = {"verdict": "escalate", "confidence": 0.0, "reasoning": f"investigate error: {exc}"}
        verdict.update({"content_hash": env["content_hash"], "rule_id": f"blindspot:{env['kind']}",
                        "file": env["uri"], "line": env["line"], "rank": i})
        verdicts.append(verdict)
        print(f"  #{i} {env['uri'].split('/')[-1]}:{env['line']} ({env['kind']}) -> {verdict.get('verdict')}")
    with open(os.path.join(out_dir, "gap_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    if backend == "dry-run":
        print(f"investigate: wrote {len(manifest)} investigation prompts -> {os.path.relpath(out_dir, root)}/")
        print("  (dry-run: no model, no key — your agent verifies these. --backend calls a model only when no agent is present.)")
        return 0
    with open(verdicts_path, "w", encoding="utf-8") as fh:
        json.dump({"verdicts": verdicts}, fh, indent=2)
    n = record_verdicts(verdicts, store_path, expiry_days)
    tally = {}
    for v in verdicts:
        tally[v.get("verdict", "?")] = tally.get(v.get("verdict", "?"), 0) + 1
    print(f"investigate: {len(verdicts)} verdicts {tally} -> {os.path.relpath(verdicts_path, root)}")
    return 0


# --------------------------------------------------------------------------- #
# backends
# --------------------------------------------------------------------------- #
def call_claude_cli(system: str, prompt: str, model: str) -> dict:
    cmd = ["claude", "-p", f"{system}\n\n{prompt}", "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    text = out.stdout
    # `claude -p --output-format json` wraps the reply in an envelope; the model
    # text is in .result — unwrap it before pulling out the verdict JSON.
    try:
        env = json.loads(text)
        if isinstance(env, dict) and isinstance(env.get("result"), str):
            text = env["result"]
    except ValueError:
        pass
    return _extract_json(text)


def call_anthropic_api(system: str, prompt: str, model: str) -> dict:
    try:
        import anthropic  # type: ignore
    except ImportError:
        raise SystemExit("anthropic-api backend needs `pip install anthropic`")
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model or "claude-opus-4-8", max_tokens=1024, system=system,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return _extract_json(text)


def _extract_json(text: str) -> dict:
    """Pull the verdict object out of the model reply, even if prose (which may
    itself contain braces) surrounds it. Scans each '{' and returns the first
    that decodes to a JSON object."""
    text = text or ""
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = dec.raw_decode(text[i:])
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return {"verdict": "escalate", "confidence": 0.0,
            "reasoning": "no parseable JSON object in model reply", "raw": text[:500]}


# --------------------------------------------------------------------------- #
# verdict recording (close the loop into the suppression store)
# --------------------------------------------------------------------------- #
def record_verdicts(verdicts: list[dict], store_path: str, expiry_days: int) -> int:
    dismissals = []
    for v in verdicts:
        if str(v.get("verdict", "")).lower() in suppress.DISMISSED:
            dismissals.append({
                "content_hash": v.get("content_hash"),
                "verdict": "dismiss",
                "rule_id": v.get("rule_id"),
                "file": v.get("file"),
                "by": "agent",
                "note": (v.get("reasoning") or "")[:300],
            })
    if dismissals:
        suppress.record_dismissals(store_path, dismissals, default_expiry_days=expiry_days)
    return len(dismissals)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Emit verifier prompts for the top-N beacons (optional headless verification; default writes files, no model, no key).")
    ap.add_argument("ranked", nargs="?", help="ranked beacon SARIF (from rank.py)")
    ap.add_argument("--backend", default=None, help="dry-run | claude-cli | anthropic-api")
    ap.add_argument("--top-n", type=int, default=None)
    ap.add_argument("--config", default=None)
    ap.add_argument("--base", default=S.repo_root())
    ap.add_argument("--out-dir", default=None, help="where dry-run prompts are written")
    ap.add_argument("--record", default=None, help="ingest a verdicts.json into the store and exit")
    ap.add_argument("--investigate", action="store_true",
                    help="dispatch the ranked BLIND SPOTS (coverage.py) instead of beacons — the LLM dark zone")
    ap.add_argument("--blindspots", default=None, help="blindspots.json path (default reports/blindspots.json)")
    a = ap.parse_args(argv)

    config = S.load_config(a.config)
    root = S.repo_root()
    dcfg = config.get("dispatch", {})
    supp_cfg = config.get("suppression", {})
    store_path = os.path.join(root, supp_cfg.get("store", "suppression/store.json"))
    expiry_days = supp_cfg.get("default_expiry_days", 90)
    verdicts_path = os.path.join(root, dcfg.get("verdicts", "reports/verdicts.json"))

    # close-the-loop-only mode
    if a.record:
        with open(a.record, encoding="utf-8") as fh:
            verdicts = json.load(fh)
        verdicts = verdicts.get("verdicts", verdicts) if isinstance(verdicts, dict) else verdicts
        n = record_verdicts(verdicts, store_path, expiry_days)
        print(f"dispatch: recorded {n} dismissal(s) into {os.path.relpath(store_path, root)}")
        return 0

    # blind-spot dark-zone mode (reads coverage.py output, not ranked beacons)
    if a.investigate:
        backend = a.backend or dcfg.get("backend", "dry-run")
        pad = dcfg.get("context_lines", 8)
        model = dcfg.get("model", "claude-opus-4-8")
        out_dir = a.out_dir or os.path.join(root, "reports", "dispatch")
        bs = a.blindspots or os.path.join(root, "reports", "blindspots.json")
        ccfg = config.get("coverage", {}) or {}
        top_k = a.top_n if a.top_n is not None else ccfg.get("top_k", 25)
        min_rel = float(ccfg.get("min_relevance", 0.6))
        return investigate(bs, a.base, backend, top_k, pad, model, out_dir,
                           verdicts_path, store_path, expiry_days, root, min_rel)

    if not a.ranked:
        ap.error("ranked SARIF path required (or use --record)")

    backend = a.backend or dcfg.get("backend", "dry-run")
    top_n = a.top_n if a.top_n is not None else dcfg.get("budget_top_n", 25)
    pad = dcfg.get("context_lines", 8)
    model = dcfg.get("model", "claude-opus-4-8")
    out_dir = a.out_dir or os.path.join(root, "reports", "dispatch")

    sarif = S.read_sarif(a.ranked)
    runs = sarif.get("runs") or [{}]
    beacons = list((runs[0] or {}).get("results", []) or [])[:top_n]
    print(f"dispatch: backend={backend}  budget=top {top_n}  beacons={len(beacons)}")

    os.makedirs(out_dir, exist_ok=True)
    for stale in glob.glob(os.path.join(out_dir, "*.md")):   # clear last run's prompts
        os.remove(stale)
    manifest, verdicts = [], []
    for b in beacons:
        env = build_envelope(b, a.base, pad)
        prompt = render_prompt(env)
        rank = env["rank"] or 0
        ch = env["content_hash"] or "nohash"
        stem = f"{rank:03d}_{ch[:10]}"
        # always write the prompt artifact (auditable, and the dry-run output)
        with open(os.path.join(out_dir, stem + ".md"), "w", encoding="utf-8") as fh:
            fh.write(f"<!-- SYSTEM -->\n{SYSTEM_PROMPT}\n\n<!-- USER -->\n{prompt}")
        manifest.append({"rank": rank, "file": env["uri"], "line": env["start"],
                         "content_hash": env["content_hash"], "axes": env["axes"],
                         "hypothesis": env["hypothesis"], "prompt_file": stem + ".md"})

        if backend == "dry-run":
            continue
        try:
            if backend == "claude-cli":
                verdict = call_claude_cli(SYSTEM_PROMPT, prompt, model)
            elif backend == "anthropic-api":
                verdict = call_anthropic_api(SYSTEM_PROMPT, prompt, model)
            else:
                raise SystemExit(f"unknown backend: {backend}")
        except Exception as exc:  # keep going; one bad beacon must not abort the run
            verdict = {"verdict": "escalate", "confidence": 0.0, "reasoning": f"dispatch error: {exc}"}
        verdict.update({"content_hash": env["content_hash"], "rule_id": b.get("ruleId"),
                        "file": env["uri"], "line": env["start"], "rank": rank})
        verdicts.append(verdict)
        print(f"  #{rank} {env['uri'].split('/')[-1]}:{env['start']} -> {verdict.get('verdict')}")

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    if backend == "dry-run":
        print(f"dispatch: wrote {len(manifest)} verifier prompts -> {os.path.relpath(out_dir, root)}/")
        print("  (dry-run: no model, no key — your agent verifies these. Set a --backend only for headless runs with no agent.)")
        return 0

    with open(verdicts_path, "w", encoding="utf-8") as fh:
        json.dump({"verdicts": verdicts}, fh, indent=2)
    n = record_verdicts(verdicts, store_path, expiry_days)
    tally = {}
    for v in verdicts:
        tally[v.get("verdict", "?")] = tally.get(v.get("verdict", "?"), 0) + 1
    print(f"dispatch: {len(verdicts)} verdicts {tally} -> {os.path.relpath(verdicts_path, root)}")
    print(f"  recorded {n} dismissal(s) into the suppression store")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
