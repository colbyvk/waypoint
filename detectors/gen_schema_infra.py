#!/usr/bin/env python3
"""
gen_schema_infra.py — generate the beacon-schema docs under schema-infra/.

Reads the rules themselves (infra/**/*.yaml) + tag_map.yaml + the sample
fixtures, and writes one Markdown schema per beacon:
  schema-infra/<language>/<classifier>/<rule-id>.md   (custom Semgrep beacons)
  schema-infra/off-the-shelf/<tool>.md                (wired-tool beacons)
  schema-infra/INDEX.md                               (every beacon, grouped)

Each doc records what the beacon is, WHERE THE DETECTION CODE LIVES, and WHICH
LINTER(S) RAISE IT — derived from source so it never drifts. schema-infra/README.md
(the shared schema) is hand-written and left untouched.

Run after changing rules:  python detectors/gen_schema_infra.py
"""
from __future__ import annotations
import glob
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sariflib as S  # noqa: E402

ROOT = S.repo_root()
INFRA = os.path.join(ROOT, "infra")
OUT = os.path.join(ROOT, "schema-infra")
SAMPLES = os.path.join(ROOT, "samples", "monorepo")

_SEV_LEVEL = {"ERROR": "error", "WARNING": "warning", "INFO": "note"}

# How each wired tool's output becomes SARIF (for the off-the-shelf docs).
_TOOL_INGEST = {
    "bandit": "JSON → `detectors/normalize/bandit_to_sarif.py`",
    "ruff": "native SARIF (`ruff check --output-format sarif`)",
    "mypy": "text → `detectors/normalize/mypy_to_sarif.py`",
    "clippy": "cargo JSON → `detectors/normalize/clippy_to_sarif.py`",
    "cargo-geiger": "JSON → `detectors/normalize/geiger_to_sarif.py`",
    "pip-audit": "JSON → `detectors/normalize/pipaudit_to_sarif.py`",
    "cargo-audit": "JSON (advisory) → normalizer",
    "trivy": "native SARIF (`trivy fs --format sarif`)",
    "osv-scanner": "native SARIF",
    "npm-audit": "JSON → normalizer",
    "gitleaks": "native SARIF (`--report-format sarif`)",
    "eslint": "native SARIF (`@microsoft/eslint-formatter-sarif`)",
    "codeql": "native SARIF",
    "cargo-mutants": "outcomes.json → `detectors/normalize/mutants_to_sarif.py`",
    "race-detector": "Go `-race` / TSan text → `detectors/normalize/race_to_sarif.py`",
    "fuzz": "cargo-fuzz / atheris / jazzer.js crash text → `detectors/normalize/fuzz_to_sarif.py` (carries the crashing input)",
    "hypothesis": "pytest+Hypothesis output → `detectors/normalize/hypothesis_to_sarif.py` (carries the shrunk reproducing input)",
    "proptest": "cargo test (proptest/quickcheck) output → `detectors/normalize/proptest_to_sarif.py` (carries the minimal failing input)",
    "fast-check": "jest/vitest+fast-check output → `detectors/normalize/fastcheck_to_sarif.py` (carries the counterexample)",
}

# Curated off-the-shelf overlaps: keyword found in a custom rule's id/hypothesis
# -> other detectors that flag the same shape (only when those tools are wired).
_RELATED = {
    "sql": ["bandit `B608` (SQL injection)", "ruff `S608` (hardcoded-sql)"],
    "eval": ["bandit `B307` (eval)", "ruff `S307` (suspicious-eval)",
             "eslint `security/detect-eval-with-expression`"],
    "exec": ["bandit `B102` (exec_used)"],
    "subprocess": ["bandit `B602`–`B607`", "ruff `S602`–`S607`"],
    "shell": ["bandit `B605` (start_process_with_a_shell)"],
    "command": ["eslint `security/detect-child-process`"],
    "child_process": ["eslint `security/detect-child-process`"],
    "tls": ["bandit `B501` (request_with_no_cert_validation)", "ruff `S501`"],
    "verify": ["bandit `B501`", "ruff `S501`"],
    "secret": ["gitleaks (secret scan)", "bandit `B105`–`B107`", "trivy (secret)"],
    "pickle": ["bandit `B301`/`B302` (pickle)"],
    "deserial": ["bandit `B301`/`B302`"],
    "yaml": ["bandit `B506` (yaml_load)"],
    "md5": ["bandit `B303`/`B324` (weak hash)"],
    "sha1": ["bandit `B303`/`B324` (weak hash)"],
    "crypto": ["bandit `B303`/`B324`/`B413`"],
    "random": ["bandit `B311` (random)", "ruff `S311`"],
    "path": ["bandit `B108`", "eslint `security/detect-non-literal-fs-filename`"],
    "traversal": ["eslint `security/detect-non-literal-fs-filename`"],
    "unwrap": ["clippy `clippy::unwrap_used`"],
    "panic": ["clippy `clippy::panic` / `clippy::unwrap_used`"],
    "expect": ["clippy `clippy::expect_used`"],
    "static mut": ["clippy `clippy::static_mut_refs`"],
    "transmute": ["clippy `clippy::transmute_*`"],
    "redos": ["eslint `security/detect-unsafe-regex`"],
    "regex": ["eslint `security/detect-unsafe-regex`"],
    "innerhtml": ["eslint `security/detect-disable-mustache-escape`"],
    "xss": ["eslint `security/*`"],
    "non-null": ["mypy (`union-attr`)", "eslint `@typescript-eslint/no-non-null-assertion`"],
    "null": ["mypy (`union-attr`, None-deref)"],
    "except": ["ruff `E722` (bare-except), `S110`, `BLE001` (blind-except)"],
    "swallow": ["ruff `S110`/`BLE001`", "bandit `B110`"],
    "effect": ["eslint `react-hooks/exhaustive-deps`"],
    "deps": ["eslint `react-hooks/exhaustive-deps`"],
    "datetime": ["ruff `DTZ*` (naive datetime)"],
    "mutable default": ["ruff `B006`", "bandit (n/a)"],
    "timeout": ["bandit `B113` (request_without_timeout)"],
}


def severity_prior(level: str, config: dict) -> float:
    return (config.get("severity_prior_map") or {}).get(level, 0.3)


def related_detectors(rule_id: str, hypothesis: str) -> list[str]:
    text = f"{rule_id} {hypothesis}".lower()
    hits: list[str] = []
    for kw, dets in _RELATED.items():
        # whole-token match so "exec" doesn't match "execute", "sql" not "sqlx", etc.
        if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", text):
            for d in dets:
                if d not in hits:
                    hits.append(d)
    return hits


def find_sample(rule_id: str) -> tuple[str, str] | None:
    """Locate a planted example for this rule and return (lang, snippet)."""
    marker = f"WAYPOINT-PLANT: {rule_id}"
    for path in glob.glob(os.path.join(SAMPLES, "**", "*"), recursive=True):
        if not os.path.isfile(path):
            continue
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            if marker in line:
                lang = {".py": "python", ".rs": "rust", ".ts": "typescript",
                        ".tsx": "tsx"}.get(os.path.splitext(path)[1], "")
                lo, hi = i, min(len(lines), i + 3)   # marker + the flagged lines
                rel = os.path.relpath(path, ROOT)
                snippet = f"# {rel}\n" if lang == "python" else f"// {rel}\n"
                return lang, snippet + "\n".join(lines[lo:hi])
    return None


def find_hazard(rule_id: str) -> str | None:
    core = rule_id.replace("waypoint-", "")
    cands = [core] + [re.sub(r"^(py|rust|ts|react)-", "", core)]
    for c in cands:
        p = os.path.join(ROOT, "hazards", f"{c}.md")
        if os.path.exists(p):
            return os.path.relpath(p, ROOT)
    return None


def iter_custom_rules():
    for f in sorted(glob.glob(os.path.join(INFRA, "**", "*.yaml"), recursive=True)):
        rel = os.path.relpath(f, ROOT)
        parts = rel.split(os.sep)            # infra / <language> / <classifier> / file
        if len(parts) < 4:
            continue
        language, classifier = parts[1], parts[2]
        try:
            data = S.load_yaml(f) or {}
        except Exception as exc:                       # tolerate a malformed file
            print(f"gen_schema_infra: skipping unparseable {rel}: {exc}", file=sys.stderr)
            continue
        for rule in (data.get("rules", []) or []):
            if isinstance(rule, dict) and rule.get("id"):
                yield language, classifier, rel, rule


def write_rule_doc(language, classifier, rel_path, rule, config) -> dict:
    rid = rule.get("id", "unknown")
    meta = rule.get("metadata", {}) or {}
    axes = meta.get("waypoint_axes", [meta.get("category", "edge-case")])
    hyp = meta.get("waypoint_hypothesis", "")
    sev = (rule.get("severity") or "WARNING").upper()
    level = _SEV_LEVEL.get(sev, "warning")
    prior = severity_prior(level, config)
    langs = ", ".join(rule.get("languages", [language]))
    related = related_detectors(rid, hyp)
    sample = find_sample(rid)
    hazard = find_hazard(rid)

    out_dir = os.path.join(OUT, language, classifier)
    os.makedirs(out_dir, exist_ok=True)
    lines = [
        f"# `{rid}`",
        "",
        f"> Beacon schema — generated from `{rel_path}` by "
        f"`detectors/gen_schema_infra.py`. Do not edit by hand.",
        "",
        f"- **Axes:** {', '.join(axes)}",
        f"- **Severity:** `{sev}` → SARIF `{level}` → `severity_prior` ≈ {prior}",
        f"- **Category:** {meta.get('category', classifier)}",
        f"- **Language(s):** {langs}",
        "",
        "## Agent hypothesis",
        f"> {hyp}" if hyp else "> _(uses the rule message)_",
        "",
        "## Where the detection code lives",
        f"- **Rule:** [`{rel_path}`]({os.path.relpath(os.path.join(ROOT, rel_path), out_dir)}) "
        f"— Semgrep rule `{rid}`",
        "- **Engine:** Semgrep, run by `detectors/run_all.sh`; its JSON is converted to "
        "SARIF (preserving these axes) by `detectors/normalize/semgrep_to_sarif.py`.",
        "",
        "## Which linters raise this beacon",
        f"- **Primary:** Semgrep — rule `{rid}`",
    ]
    if related:
        lines.append("- **Also flagged by (when that tool is installed):** "
                     + "; ".join(related))
    lines += [
        "",
        "## Beacon this rule emits",
        "```jsonc",
        f'{{ "ruleId": "{rid}", "level": "{level}",',
        f'  "properties": {{ "waypoint": {{',
        f'    "axes": {json.dumps(axes)}, "severity_prior": {prior},',
        f'    "hypothesis": "{hyp}",',
        '    "content_hash": "…", "tool": "semgrep", "rule_id": "' + rid + '" }} }}',
        "```",
        "`score` / `rank` / `boundary_reachable` / `centrality` are added by "
        "`prioritise/rank.py`; `merged_from` lists every detector if this region "
        "is deduped with another tool. See [the shared schema](../../README.md).",
    ]
    if sample:
        lang, snippet = sample
        lines += ["", "## Example region it fires on", f"```{lang}", snippet, "```"]
    if hazard:
        lines += ["", "## See also",
                  f"- Plain-English hazard: [`{hazard}`]"
                  f"({os.path.relpath(os.path.join(ROOT, hazard), out_dir)})"]
    lines.append("")
    with open(os.path.join(out_dir, f"{rid}.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return {"rule_id": rid, "language": language, "classifier": classifier,
            "axes": axes, "hypothesis": hyp, "level": level}


def write_offtheshelf(tag_map) -> list[dict]:
    out_dir = os.path.join(OUT, "off-the-shelf")
    os.makedirs(out_dir, exist_ok=True)
    docs = []
    tools = (tag_map.get("tools") or {})
    for tool, block in sorted(tools.items()):
        default = block.get("_default", {})
        ingest = _TOOL_INGEST.get(tool, "normalized to SARIF")
        lines = [
            f"# `{tool}` beacons (off-the-shelf detector)",
            "",
            f"> Generated from `tag_map.yaml`. Waypoint runs **{tool}** as-is "
            "(spec §13: install, don't reimplement) and tags its findings.",
            "",
            "## Where the detection code lives",
            f"- **Engine:** the `{tool}` tool and its built-in rule packs (not Waypoint code).",
            f"- **Into SARIF via:** {ingest}.",
            f"- **Tagged by:** `tag_map.yaml` → `tools.{tool}`.",
            "",
            f"- **Default axes:** {', '.join(default.get('axes', ['edge-case']))}",
            f"- **Default hypothesis:** {default.get('hypothesis', '(rule message)')}",
            "",
            "## Rule-id → axes mapping (`tag_map.yaml`)",
            "| rule-id match | axes | agent hypothesis |",
            "|---|---|---|",
        ]
        for entry in block.get("rules", []) or []:
            lines.append(f"| `{entry.get('match','')}` | {', '.join(entry.get('axes', []))} "
                         f"| {entry.get('hypothesis','')} |")
        if not (block.get("rules")):
            lines.append("| _(default only)_ | — | — |")
        lines.append("")
        with open(os.path.join(out_dir, f"{tool}.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        docs.append({"tool": tool, "axes": default.get("axes", [])})
    return docs


def write_index(rule_docs, tool_docs):
    by = {}
    for d in rule_docs:
        by.setdefault(d["language"], {}).setdefault(d["classifier"], []).append(d)
    lines = ["# Beacon index", "",
             "Every beacon Waypoint can raise. Custom Semgrep beacons are grouped by "
             "language × axis; off-the-shelf beacons come from the wired tools. See "
             "[the shared schema](README.md).", "",
             f"**{len(rule_docs)} custom beacons · {len(tool_docs)} wired tools.**", ""]
    for language in sorted(by):
        lines.append(f"## {language}")
        for classifier in sorted(by[language]):
            lines.append(f"### {classifier}")
            lines.append("| beacon | axes | hypothesis |")
            lines.append("|---|---|---|")
            for d in sorted(by[language][classifier], key=lambda x: x["rule_id"]):
                link = f"{language}/{classifier}/{d['rule_id']}.md"
                lines.append(f"| [`{d['rule_id']}`]({link}) | {', '.join(d['axes'])} "
                             f"| {d['hypothesis']} |")
            lines.append("")
    lines.append("## Off-the-shelf detectors")
    lines.append("| tool | default axes | doc |")
    lines.append("|---|---|---|")
    for t in sorted(tool_docs, key=lambda x: x["tool"]):
        lines.append(f"| {t['tool']} | {', '.join(t['axes'])} "
                     f"| [off-the-shelf/{t['tool']}.md](off-the-shelf/{t['tool']}.md) |")
    lines.append("")
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    config = S.load_config()
    tag_map = S.load_yaml(os.path.join(ROOT, config.get("tag_map", "tag_map.yaml")))

    # clear generated content, keep the hand-written README
    for entry in os.listdir(OUT) if os.path.isdir(OUT) else []:
        p = os.path.join(OUT, entry)
        if entry == "README.md":
            continue
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    rule_docs = [write_rule_doc(lang, cls, rel, rule, config)
                 for lang, cls, rel, rule in iter_custom_rules()]
    tool_docs = write_offtheshelf(tag_map)
    write_index(rule_docs, tool_docs)
    print(f"gen_schema_infra: {len(rule_docs)} custom beacon schemas + "
          f"{len(tool_docs)} off-the-shelf tool docs -> schema-infra/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
