"""
sariflib — the one place Waypoint knows how to read and write SARIF.

Every custom Waypoint script (merge_sarif.py, rank.py, fallback_dispatcher.py,
the normalize/ wrappers) imports this module so there is exactly ONE
implementation of "what is a beacon and where does it live in SARIF". If a tool
emits a SARIF dialect we mishandle, fix it HERE and every stage benefits.

A beacon is a SARIF `result`. Waypoint's extra fields (axes, severity prior,
hypothesis, content hash, score, ...) live in `result.properties.waypoint`.
We never invent a top-level schema — SARIF already carries location, rule id,
level and message (spec §2.2).

Pure standard library except PyYAML (for config/allowlist). No SWE-only deps.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
from typing import Any, Iterator

try:
    import yaml  # PyYAML — used only for config + allowlist
except ImportError:  # pragma: no cover - guidance for the owning team
    raise SystemExit(
        "PyYAML is required. Activate the project venv (.venv) or run "
        "detectors/install.sh, then retry."
    )

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"

# The single namespace under result.properties where all Waypoint fields live.
WP = "waypoint"

# Detection axes (spec §3.2). The first four are the security-oriented axes
# every beacon is tagged against; `logic` carries DYNAMIC correctness evidence —
# surviving mutants, observed data races, fuzz crashes, and property-test
# counterexamples (see detectors/run_logic.sh). Anything outside this set
# becomes a free-form sub-tag.
AXES = (
    "security", "edge-case", "concurrency", "abuse",
    "logic",                                   # dynamic logic evidence: surviving
                                               # mutants, data races, fuzz crashes,
                                               # property-test counterexamples
                                               # (see detectors/run_logic.sh)
)


# --------------------------------------------------------------------------- #
# config / yaml
# --------------------------------------------------------------------------- #
def repo_root() -> str:
    """Absolute path to the waypoint/ repo root (parent of detectors/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(path: str | None = None) -> dict:
    """Load waypoint.config.yaml (defaults to the one at the repo root)."""
    path = path or os.path.join(repo_root(), "waypoint.config.yaml")
    return load_yaml(path)


# --------------------------------------------------------------------------- #
# SARIF read / write / build
# --------------------------------------------------------------------------- #
def read_sarif(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_sarif(sarif: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(sarif, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def empty_sarif(tool_name: str, rules: list[dict] | None = None) -> dict:
    """A well-formed empty SARIF 2.1.0 log with one run for `tool_name`."""
    return {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": "https://github.com/your-org/waypoint",
                        "rules": rules or [],
                    }
                },
                "results": [],
            }
        ],
    }


def physical_location(uri: str, start_line: int = 1, end_line: int | None = None,
                       start_col: int | None = None, end_col: int | None = None) -> dict:
    """Build a SARIF physicalLocation. Used by the normalize/ wrappers."""
    region: dict = {"startLine": max(1, int(start_line or 1))}
    if end_line:
        region["endLine"] = max(region["startLine"], int(end_line))
    if start_col:
        region["startColumn"] = int(start_col)
    if end_col:
        region["endColumn"] = int(end_col)
    return {"physicalLocation": {"artifactLocation": {"uri": uri}, "region": region}}


def make_result(rule_id: str, level: str, message: str, uri: str,
                start_line: int = 1, end_line: int | None = None,
                start_col: int | None = None, end_col: int | None = None,
                properties: dict | None = None) -> dict:
    """Build a SARIF result object from primitives (for normalize/ wrappers)."""
    res: dict = {
        "ruleId": rule_id,
        "level": level if level in ("error", "warning", "note", "none") else "warning",
        "message": {"text": message or rule_id},
    }
    if uri:
        if start_line:
            res["locations"] = [physical_location(uri, start_line, end_line, start_col, end_col)]
        else:
            # finding with no meaningful line (e.g. dependency manifest)
            res["locations"] = [{"physicalLocation": {"artifactLocation": {"uri": uri}}}]
    if properties:
        res["properties"] = properties
    return res


def iter_results(sarif: dict) -> Iterator[tuple[dict, dict]]:
    """Yield (run, result) for every result across every run."""
    for run in sarif.get("runs", []) or []:
        for result in run.get("results", []) or []:
            yield run, result


def tool_name(run: dict) -> str:
    return (((run.get("tool") or {}).get("driver") or {}).get("name")) or "unknown"


# --------------------------------------------------------------------------- #
# result accessors (handle the dialect differences between tools)
# --------------------------------------------------------------------------- #
def result_rule_id(result: dict) -> str:
    rid = result.get("ruleId")
    if rid:
        return rid
    # some tools only set rule.id inside the result
    rule = result.get("rule") or {}
    return rule.get("id") or "unknown"


def result_message(result: dict) -> str:
    msg = result.get("message") or {}
    if isinstance(msg, dict):
        return (msg.get("text") or msg.get("markdown") or "").strip()
    return str(msg).strip()


def driver_rules(run: dict) -> list[dict]:
    return (((run.get("tool") or {}).get("driver") or {}).get("rules")) or []


def result_rule_metadata(run: dict, result: dict) -> dict:
    """Resolve the rule object for a result and return its properties bag.

    Tools reference their rule by ruleIndex (into driver.rules) or by ruleId.
    Custom Waypoint Semgrep rules stash waypoint_axes / waypoint_hypothesis in
    rule.properties; this is how those reach the beacon.
    """
    rules = driver_rules(run)
    idx = result.get("ruleIndex")
    rule = None
    if isinstance(idx, int) and 0 <= idx < len(rules):
        rule = rules[idx]
    if rule is None:
        rid = result_rule_id(result)
        for r in rules:
            if r.get("id") == rid or r.get("name") == rid:
                rule = r
                break
    if rule is None:
        return {}
    rp = rule.get("properties")
    # Semgrep nests its rule metadata under properties; some emit it flat.
    return dict(rp) if isinstance(rp, dict) else {}


def result_level(result: dict, run: dict) -> str:
    """Normalized SARIF level: error | warning | note | none."""
    lvl = result.get("level")
    if lvl in ("error", "warning", "note", "none"):
        return lvl
    # Fall back to the rule's defaultConfiguration.level
    rules = driver_rules(run)
    idx = result.get("ruleIndex")
    if isinstance(idx, int) and 0 <= idx < len(rules):
        dc = (rules[idx].get("defaultConfiguration") or {})
        if dc.get("level") in ("error", "warning", "note", "none"):
            return dc["level"]
    return "warning"


# --------------------------------------------------------------------------- #
# locations
# --------------------------------------------------------------------------- #
def _strip_uri(uri: str) -> str:
    if uri.startswith("file://"):
        uri = uri[len("file://"):]
    # semgrep/codeql sometimes prefix a uriBaseId token like %SRCROOT%/
    uri = re.sub(r"^%[A-Z_]+%/?", "", uri)
    return uri


def result_location(result: dict) -> dict:
    """Primary physical location as a flat dict.

    Returns {uri, start_line, end_line, start_col, end_col}. Missing pieces
    default sensibly (end_line=start_line, columns None). uri is whatever the
    tool reported, lightly cleaned; use resolve_path() to get an on-disk path.
    """
    locs = result.get("locations") or []
    if not locs:
        return {"uri": "", "start_line": 0, "end_line": 0,
                "start_col": None, "end_col": None}
    phys = (locs[0].get("physicalLocation") or {})
    art = (phys.get("artifactLocation") or {})
    region = (phys.get("region") or {})
    start_line = int(region.get("startLine") or 0)
    end_line = int(region.get("endLine") or start_line or 0)
    return {
        "uri": _strip_uri(art.get("uri") or ""),
        "start_line": start_line,
        "end_line": max(end_line, start_line),
        "start_col": region.get("startColumn"),
        "end_col": region.get("endColumn"),
    }


def result_symbol(result: dict) -> str | None:
    """Enclosing symbol from logicalLocations, if the tool provided one."""
    locs = result.get("locations") or []
    if locs:
        logical = locs[0].get("logicalLocations") or []
        if logical:
            ll = logical[0]
            return ll.get("fullyQualifiedName") or ll.get("name")
    return None


# Per-extension regexes that match a symbol *definition* line. Used to find the
# enclosing symbol of a region (for agent hypotheses and centrality). Each
# pattern's last group is the symbol name. Approximate by design (spec §7:
# "do not over-engineer this").
_DEF_PATTERNS = {
    ".py": [re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\("),
            re.compile(r"^\s*class\s+(\w+)")],
    ".rs": [re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+(\w+)"),
            re.compile(r"^\s*impl(?:\s+\w+\s+for)?\s+(\w+)"),
            re.compile(r"^\s*(?:pub\s+)?struct\s+(\w+)")],
    ".ts": [re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)"),
            re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*="),
            re.compile(r"^\s*(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*[:{]")],
}
_DEF_PATTERNS[".tsx"] = _DEF_PATTERNS[".ts"]
_DEF_PATTERNS[".jsx"] = _DEF_PATTERNS[".ts"]
_DEF_PATTERNS[".js"] = _DEF_PATTERNS[".ts"]


def enclosing_symbol(base: str, loc: dict) -> str | None:
    """Nearest enclosing function/class/impl name for a region.

    Prefers a logicalLocation if the tool emitted one; otherwise scans upward
    from the region's start line for a definition line matching the file's
    language patterns. Returns None if nothing is found.
    """
    path = resolve_path(loc.get("uri", ""), base)
    if not path or not os.path.isfile(path):
        return None
    ext = os.path.splitext(path)[1].lower()
    patterns = _DEF_PATTERNS.get(ext)
    if not patterns:
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    start = min(max(1, loc.get("start_line") or 1), len(lines))
    for i in range(start - 1, -1, -1):
        line = lines[i]
        for pat in patterns:
            m = pat.match(line)
            if m:
                return m.group(1)
    return None


def resolve_path(uri: str, base: str) -> str | None:
    """Map a SARIF uri to an on-disk path UNDER `base`. Returns None if the
    resolved path escapes `base` — via `..` traversal OR a symlink that points
    out of the tree. Waypoint only ever reads files inside the scanned directory,
    so a crafted tool output / SARIF can't make it read e.g. /etc/passwd."""
    if not uri:
        return None
    uri = _strip_uri(uri)
    cand = uri if os.path.isabs(uri) else os.path.join(base, uri)
    if not os.path.exists(cand):
        return None
    # realpath() resolves '..' and follows symlinks, so the containment check
    # blocks both traversal and a symlink inside the tree aimed outside it.
    try:
        real = os.path.realpath(cand)
        base_real = os.path.realpath(base)
    except OSError:
        return None
    if real == base_real or real.startswith(base_real + os.sep):
        return cand
    return None


# --------------------------------------------------------------------------- #
# region text, normalization, content hash (the heart of suppression §9)
# --------------------------------------------------------------------------- #
def region_text(base: str, loc: dict, pad: int = 0) -> str | None:
    """Raw source text covered by a beacon's region, optionally padded by `pad`
    lines on each side. Returns None if the file cannot be read."""
    path = resolve_path(loc.get("uri", ""), base)
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    if not lines:
        return ""
    start = max(1, (loc.get("start_line") or 1) - pad)
    end = min(len(lines), (loc.get("end_line") or start) + pad)
    if end < start:
        end = start
    return "\n".join(lines[start - 1:end])


_WS = re.compile(r"\s+")


def normalize_code(text: str) -> str:
    """Whitespace-insensitive normal form of a region.

    Reindentation, reflow, and blank-line churn must NOT change the hash (so a
    suppression survives cosmetic edits), but a real token change MUST (so the
    region is re-examined). We strip each line, collapse internal whitespace,
    and drop blank lines. Comments are intentionally kept — editing a comment
    re-raising a beacon is a safe, conservative behavior.
    """
    out = []
    for line in text.splitlines():
        s = _WS.sub(" ", line.strip())
        if s:
            out.append(s)
    return "\n".join(out)


# Dependency/lock manifests. Findings here (CVEs) are identified by advisory,
# not by a source region — many distinct advisories share the same line.
_MANIFESTS = ("requirements*.txt", "Pipfile*", "poetry.lock", "package.json",
              "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.toml",
              "Cargo.lock", "go.mod", "go.sum", "Gemfile*", "composer.json",
              "composer.lock", "*.lock")


def is_manifest(uri: str) -> bool:
    bn = os.path.basename(uri or "")
    return any(fnmatch.fnmatch(bn, p) for p in _MANIFESTS)


def content_hash(base: str, result: dict) -> str:
    """Stable hash of the normalized region a beacon covers (spec §9).

    Falls back to a hash of (rule id + message + uri) when there is no readable
    source region — e.g. dependency-CVE beacons that point at a manifest, or a
    file that has since been deleted. This keeps DISTINCT advisories on the same
    manifest line apart (their rule id/message differ) and stops one dismissal
    from suppressing every CVE in the file. Every beacon always has a hash.
    """
    loc = result_location(result)
    uri = loc.get("uri", "")
    # no real region, or a dependency manifest -> identify by advisory, not line
    if not loc.get("start_line") or is_manifest(uri):
        seed = "|".join([result_rule_id(result), result_message(result), uri])
        return "fallback:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]
    text = region_text(base, loc)
    if text is None:
        seed = "|".join([
            result_rule_id(result),
            result_message(result),
            loc.get("uri", ""),
        ])
        return "fallback:" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]
    norm = normalize_code(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:24]


# --------------------------------------------------------------------------- #
# severity prior
# --------------------------------------------------------------------------- #
def severity_prior(result: dict, run: dict, config: dict) -> float:
    """The detector's cheap pre-agent severity guess, 0..1.

    Precedence: explicit waypoint metadata > CVSS security-severity property >
    SARIF level mapping from config.
    """
    meta = result_rule_metadata(run, result)
    props = result.get("properties")
    props = props if isinstance(props, dict) else {}
    # explicit waypoint prior wins, from rule metadata OR the result bag (same
    # convention as waypoint_axes — a rule author may set it in either place)
    explicit = meta.get("waypoint_severity_prior", props.get("waypoint_severity_prior"))
    if explicit is not None:
        try:
            return float(explicit)
        except (TypeError, ValueError):
            pass
    sec = props.get("security-severity")
    if sec is not None:
        try:
            return max(0.0, min(1.0, float(sec) / 10.0))
        except (TypeError, ValueError):
            pass
    # Per-rule prior overrides for KNOWN low-value third-party rules (asserts,
    # style, perf). Without this they inherit the SARIF level map — a ruff S101
    # emitted at "error" gets the same 0.9 prior as a real injection, then
    # boundary/multi-axis bonuses float it to the top. Cap it at the source so it
    # stays visible (recall) but cannot outrank genuine security/logic findings.
    rid = result.get("ruleId")
    if rid:
        import fnmatch
        for pat, val in (config.get("rule_prior_overrides") or {}).items():
            if rid == pat or fnmatch.fnmatchcase(rid, pat):
                try:
                    return float(val)
                except (TypeError, ValueError):
                    pass
    level = result_level(result, run)
    return float((config.get("severity_prior_map") or {}).get(level, 0.3))


# --------------------------------------------------------------------------- #
# waypoint properties helpers
# --------------------------------------------------------------------------- #
def wp_props(result: dict) -> dict:
    """The result.properties.waypoint dict, created if absent."""
    props = result.setdefault("properties", {})
    return props.setdefault(WP, {})


def get_wp(result: dict, key: str, default: Any = None) -> Any:
    return (result.get("properties") or {}).get(WP, {}).get(key, default)


# Differential / metamorphic property relations. A property test that compares
# two execution paths — roundtrip (decode∘encode == id), idempotence (f∘f == f),
# equivalence to a reference impl (differential), commutativity — is the way to
# catch logic bugs with no spec. When such a property is falsified we label the
# beacon with the relation it broke so it's recognizable as differential/
# metamorphic evidence. Best-effort keyword match over the tool's output.
_RELATION_KEYWORDS = {
    "roundtrip": ("roundtrip", "round-trip", "round trip", "encode", "decode",
                  "serializ", "deserializ", "dumps", "loads", "to_json", "from_json"),
    "idempotent": ("idempotent", "idempoten"),
    "differential": ("differential", "equivalent", "reference impl",
                     "reference_impl", "oracle", "_ref(", "_reference("),
    "commutative": ("commutative", "commut", "associative", "binary_op", "binary-op"),
    "metamorphic": ("metamorphic", "permutation", "monotonic", "invariant under"),
}


def property_relation_subtags(text: str) -> list[str]:
    """Subtags marking a differential/metamorphic property failure, if detectable
    from the tool output (e.g. a falsified roundtrip or equivalence relation)."""
    t = (text or "").lower()
    return [name for name, kws in _RELATION_KEYWORDS.items() if any(k in t for k in kws)]


# --------------------------------------------------------------------------- #
# secret redaction — a secrets finding (gitleaks/trivy, or our hardcoded-secret
# rules) quotes the offending line, which IS the secret. Mask secret-looking
# values before they reach human-facing beacon .md files. Over-redaction is the
# safe failure mode; specific token shapes + sensitive key=value pairs only, so
# benign text (and the 24-hex content_hash) is left alone.
# --------------------------------------------------------------------------- #
_SECRET_MASK = "«redacted-secret»"
_SECRET_TOKEN_RX = [
    re.compile(r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),                                  # AWS access key id
    re.compile(r'\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b'),       # GitHub tokens
    re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b'),                               # Slack tokens
    re.compile(r'\bsk-[A-Za-z0-9]{20,}\b'),                                        # OpenAI-style keys
    re.compile(r'\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b'),  # JWT
    re.compile(r'-----BEGIN[ A-Z]*PRIVATE KEY-----'),                              # PEM private key
]
_SECRET_KV_RX = re.compile(
    r'(?i)('                                              # group 1: the sensitive key
    r'password|passwd|pwd|secret|api[_-]?key|apikey|access[_-]?key|secret[_-]?key|'
    r'token|auth|bearer|client[_-]?secret|private[_-]?key|credential'
    r')(\s*[:=]\s*|["\']\s*:\s*["\']?)([^\s"\',;)]{6,})')  # group 2: separator, group 3: the value


def redact_secrets(text: str | None) -> str | None:
    """Mask secret-looking values in human-facing text. Returns text unchanged if
    nothing matches."""
    if not text:
        return text
    out = text
    for rx in _SECRET_TOKEN_RX:
        out = rx.sub(_SECRET_MASK, out)
    out = _SECRET_KV_RX.sub(lambda m: f"{m.group(1)}{m.group(2)}{_SECRET_MASK}", out)
    return out


# --------------------------------------------------------------------------- #
# pattern matching helpers
# --------------------------------------------------------------------------- #
def imatch(value: str, pattern: str) -> bool:
    """Case-insensitive fnmatch."""
    return fnmatch.fnmatchcase((value or "").lower(), (pattern or "").lower())


def glob_match_path(path: str, patterns: list[str]) -> bool:
    p = (path or "").replace("\\", "/")
    for pat in patterns or []:
        if fnmatch.fnmatch(p, pat) or fnmatch.fnmatch("/" + p, pat):
            return True
    return False


# --------------------------------------------------------------------------- #
# lightweight structural SARIF validation (acceptance: "valid SARIF 2.1.0")
# --------------------------------------------------------------------------- #
def validate_sarif(sarif: dict) -> list[str]:
    """Return a list of structural problems; empty list means well-formed.

    Deliberately focused (not a full JSON-Schema validation) so the owning team
    can read the error messages and fix them without SWE help.
    """
    errs: list[str] = []
    if sarif.get("version") != SARIF_VERSION:
        errs.append(f"version must be {SARIF_VERSION!r}, got {sarif.get('version')!r}")
    runs = sarif.get("runs")
    if not isinstance(runs, list):
        errs.append("'runs' must be a list")
        return errs
    for ri, run in enumerate(runs):
        driver = ((run.get("tool") or {}).get("driver") or {})
        if not driver.get("name"):
            errs.append(f"runs[{ri}].tool.driver.name is missing")
        results = run.get("results")
        if results is None:
            continue
        if not isinstance(results, list):
            errs.append(f"runs[{ri}].results must be a list")
            continue
        for xi, res in enumerate(results):
            where = f"runs[{ri}].results[{xi}]"
            if not result_rule_id(res):
                errs.append(f"{where}.ruleId missing")
            if not result_message(res):
                errs.append(f"{where}.message.text missing")
            locs = res.get("locations")
            if locs and not isinstance(locs, list):
                errs.append(f"{where}.locations must be a list")
    return errs
