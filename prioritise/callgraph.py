#!/usr/bin/env python3
"""
callgraph.py — a real (not text-count) call graph for ranking.

The cheap ranker used to approximate centrality by counting how often a symbol
NAME appears followed by `(` anywhere in the repo, and boundary-reachability by
path/symbol/decorator globs. Both are heuristics that don't PROVE a region
matters. This module builds an actual call graph — caller → callee edges scoped
to each function body — and from it computes:

  * fan_in(name)         — how many DISTINCT functions call `name` (centrality)
  * reachable_from(roots)— forward BFS, the set of symbols reachable from the
                           trust-boundary entrypoints (proven reachability)

Python is parsed accurately with the stdlib `ast`. TypeScript/JavaScript/Rust
have no stdlib parser and tree-sitter may be absent, so they use a brace-scoped
regex extractor: real def→call edges, best-effort on scope. rank.py falls back
to the old text count when a symbol isn't in the graph, so nothing regresses.

Pure standard library.
"""
from __future__ import annotations

import ast
import os
import re

_PY_EXT = (".py",)
_CLIKE = {".ts": "ts", ".tsx": "ts", ".js": "ts", ".jsx": "ts", ".mjs": "ts",
          ".cjs": "ts", ".rs": "rust"}
_SKIP_DIRS = {".git", ".venv", "node_modules", "target", "reports", "__pycache__",
              "dist", "build", ".mypy_cache"}

TOPLEVEL = "<toplevel>"   # synthetic caller for module-level code (runs on import)

# identifiers that look like calls but aren't function calls we care about
_CLIKE_KEYWORDS = {
    "if", "for", "while", "switch", "catch", "return", "match", "fn", "function",
    "await", "typeof", "throw", "new", "super", "constructor", "yield", "in", "of",
    "as", "and", "or", "not", "let", "const", "var", "use", "mod", "impl", "struct",
    "enum", "where", "move", "async", "unsafe", "pub", "do", "else", "Some", "Ok",
    "Err", "None", "vec", "println", "print", "assert", "panic", "format",
}

# Python call shapes the static graph CANNOT follow (control flow becomes data) —
# the source of "blind spots" the LLM dark-zone is meant to investigate.
_DYN_NAME = {"getattr", "eval", "exec", "__import__", "compile"}      # builtin(name)
_DYN_ATTR = {"import_module", "__getattr__", "__getattribute__",      # x.import_module(var)
             "methodcaller", "attrgetter"}
# Relative priority when several dynamic shapes collapse onto one line.
_DYN_PRIORITY = {"eval": 5, "exec": 5, "getattr": 4, "__import__": 4, "compile": 4,
                 "import_module": 4, "computed-dispatch": 3, "methodcaller": 3,
                 "attrgetter": 3, "__getattr__": 2, "__getattribute__": 2,
                 "returned-callable": 1}


# --------------------------------------------------------------------------- #
# extractors
# --------------------------------------------------------------------------- #
def _dec_name(d: ast.expr) -> str:
    """Best-effort dotted name of a decorator expression (for boundary marks)."""
    if isinstance(d, ast.Call):
        d = d.func
    parts = []
    while isinstance(d, ast.Attribute):
        parts.append(d.attr)
        d = d.value
    if isinstance(d, ast.Name):
        parts.append(d.id)
    return ".".join(reversed(parts))


def _py_callees(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                names.add(f.id)
            elif isinstance(f, ast.Attribute):
                names.add(f.attr)
    return names


def _extract_python(text: str):
    """Return (defs, toplevel_calls, dynamics, parse_ok).

    defs      = list of (name, callees, line, decorators)
    dynamics  = list of {line, kind, enclosing} — dynamic-dispatch / reflection
                sites the graph cannot resolve (blind spots)
    parse_ok  = False if the file could not be parsed at all (zero coverage)
    """
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return [], set(), [], False
    defs = []
    func_nodes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_nodes.append(node)
            decs = [_dec_name(d) for d in node.decorator_list]
            defs.append((node.name, _py_callees(node), node.lineno, decs))
    # (name, lo, hi) spans so a site can be attributed to its INNERMOST function.
    named_spans = [(n.name, n.lineno, getattr(n, "end_lineno", n.lineno)) for n in func_nodes]
    fn_spans = [(lo, hi) for _, lo, hi in named_spans]

    def _enclosing(ln: int) -> str:
        best, best_w = TOPLEVEL, None
        for nm, lo, hi in named_spans:
            if lo <= ln <= hi and (best_w is None or (hi - lo) < best_w):
                best, best_w = nm, hi - lo
        return best

    top: set[str] = set()
    dynamics: list[dict] = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        ln = getattr(n, "lineno", 0)
        f = n.func
        if not any(a <= ln <= b for a, b in fn_spans):   # module-level call
            if isinstance(f, ast.Name):
                top.add(f.id)
            elif isinstance(f, ast.Attribute):
                top.add(f.attr)
        # dynamic-dispatch / reflection detection. getattr/setattr/import with a
        # STRING-LITERAL target are statically known (`getattr(o,"x")` == `o.x`) —
        # only the COMPUTED forms are blind spots.
        kind = None

        def _computed(idx: int) -> bool:
            arg = n.args[idx] if len(n.args) > idx else None
            return not (isinstance(arg, ast.Constant) and isinstance(arg.value, str))

        if isinstance(f, ast.Name) and f.id in _DYN_NAME:
            if f.id in ("getattr", "setattr"):
                if _computed(1):
                    kind = f.id
            elif f.id == "__import__":
                if _computed(0):
                    kind = f.id
            else:                                 # eval / exec / compile
                kind = f.id
        elif isinstance(f, ast.Attribute) and f.attr in _DYN_ATTR:
            if f.attr == "import_module":
                if _computed(0):
                    kind = f.attr
            else:
                kind = f.attr
        elif isinstance(f, ast.Subscript):       # table[key](...)  /  globals()[x](...)
            kind = "computed-dispatch"
        if kind:
            dynamics.append({"line": ln, "kind": kind, "enclosing": _enclosing(ln)})
    return defs, top, dynamics, True


def _python_public_names(text: str) -> set[str]:
    """The module's PUBLIC API surface: module-level functions, and methods of
    module-level classes, whose names don't start with `_`. A library's public API
    *is* its entry surface — external callers reach it — so these seed reachability
    even when there is no app-style trust boundary (handler/route/main). Sound: a
    public symbol is callable from outside the repo by definition."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return set()
    pub: set[str] = set()
    for node in tree.body:                                  # module top level only
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                pub.add(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            for item in node.body:
                if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and not item.name.startswith("_")):
                    pub.add(item.name)
    return pub


_CLIKE_DEF = re.compile(
    r"""(?:
        \bfunction\s+(?P<f>[A-Za-z_$][\w$]*)            # function foo(
      | \bfn\s+(?P<r>[A-Za-z_][\w]*)                    # rust fn foo(
      | \b(?:const|let|var)\s+(?P<c>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^()]*\)\s*(?::[^=>{]+)?=>) # const foo = (..) =>
      | ^[ \t]*(?:public|private|protected|static|async|readonly|\s)*(?P<m>[A-Za-z_$][\w$]*)\s*\([^;{)]*\)\s*\{  # class method foo(...) {
    )""",
    re.VERBOSE | re.MULTILINE,
)
_CALL_RE = re.compile(r"\b([A-Za-z_$][\w$]*)\s*\(")


def _match_brace(text: str, open_idx: int):
    """Return (end_index, closed_ok). closed_ok is False if we hit EOF without the
    brace returning to depth 0 — the body could NOT be reliably bounded. That's a
    conservative signal: such a function is treated as un-analyzable (dark) and its
    (unreliable) callees are dropped, so it can never falsely mark a target reachable.

    String- and comment-aware so braces inside `"{"`, `// {`, `/* { */` don't throw
    off the depth count — that makes body_ok a trustworthy signal, not a guess."""
    depth = 0
    i, n = open_idx, len(text)
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":                       # line comment
            j = text.find("\n", i)
            i = n if j == -1 else j
            continue
        if c == "/" and nxt == "*":                       # block comment
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        if c in "'\"`":                                    # string / template literal
            i += 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == c:
                    i += 1
                    break
                i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i, True
        i += 1
    return n - 1, False


_CLIKE_DYN = [
    (re.compile(r"\beval\s*\("), "eval"),
    (re.compile(r"\b(?:new\s+)?Function\s*\("), "function-ctor"),
    (re.compile(r"[A-Za-z_$\])][ \t]*\[[^\]\n]+\][ \t]*\("), "computed-dispatch"),  # obj[key](
    (re.compile(r"\brequire\s*\(\s*[^'\"`)\s]"), "dynamic-require"),                # require(var)
]


def _extract_clike(text: str):
    """Brace-scoped def→callee extraction for TS/JS/Rust. Best-effort.
    Returns (defs, dynamics) — dynamics mirror the Python extractor."""
    defs = []
    spans = []   # (name, body_start_char, body_end_char) for enclosing attribution
    for m in _CLIKE_DEF.finditer(text):
        name = m.group("f") or m.group("r") or m.group("c") or m.group("m")
        if not name or name in _CLIKE_KEYWORDS:
            continue
        brace = text.find("{", m.end() - 1)
        if brace == -1:
            continue
        end, body_ok = _match_brace(text, brace)
        body = text[brace + 1:end]
        callees = {c for c in _CALL_RE.findall(body) if c not in _CLIKE_KEYWORDS}
        line = text.count("\n", 0, m.start()) + 1
        defs.append((name, callees, line, [], body_ok))   # body_ok=False ⇒ conservatively dark
        spans.append((name, brace, end))

    def _enclosing(pos: int) -> str:
        best, best_w = TOPLEVEL, None
        for nm, lo, hi in spans:
            if lo <= pos <= hi and (best_w is None or (hi - lo) < best_w):
                best, best_w = nm, hi - lo
        return best

    dynamics: list[dict] = []
    for rx, kind in _CLIKE_DYN:
        for m in rx.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            dynamics.append({"line": ln, "kind": kind, "enclosing": _enclosing(m.start())})
    return defs, dynamics


_EXPORT_RX = re.compile(
    r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)"  # export [default] [async] function/class NAME
    r"|\bexport\s+(?:const|let|var)\s+([A-Za-z_$][\w$]*)"                              # export const NAME = …
    r"|\bexport\s+default\s+([A-Za-z_$][\w$]*)"                                        # export default IDENT
    r"|\bexport\s*\{([^}]*)\}"                                                          # export { a, b as c }
    r"|\bpub(?:\s*\([^)]*\))?\s+(?:async\s+)?fn\s+([A-Za-z_][\w]*)",                    # rust pub fn NAME
    re.MULTILINE,
)


def _clike_exported_names(text: str) -> set[str]:
    """Exported / public symbols for TS/JS (`export …`) and Rust (`pub fn`). These are
    the module's entry surface — seed reachability from them. For `export { a as c }`
    the LOCAL name `a` is seeded (that's what the def is keyed by)."""
    names: set[str] = set()
    for m in _EXPORT_RX.finditer(text):
        for g in (m.group(1), m.group(2), m.group(3), m.group(5)):
            if g:
                names.add(g)
        if m.group(4):                                       # export { a, b as c }
            for part in m.group(4).split(","):
                local = part.strip().split(" as ")[0].strip()
                if re.match(r"^[A-Za-z_$][\w$]*$", local):
                    names.add(local)
    return names


# tree-sitter is an OPTIONAL soundness upgrade for clike (TS/JS/TSX/JSX/Rust). When
# present it gives sound enumeration + reliable bodies; when absent we fall back to
# the regex extractor above. Python always uses stdlib `ast` (sound, zero-dep).
try:
    import treesitter_graph as _ts
except Exception:
    _ts = None

_TS_LANG = {".ts": "typescript", ".tsx": "tsx", ".js": "javascript", ".jsx": "javascript",
            ".mjs": "javascript", ".cjs": "javascript", ".rs": "rust"}


def clike_backend() -> str:
    """Which extractor clike files use: 'tree-sitter' (sound) or 'regex' (best-effort)."""
    return "tree-sitter" if (_ts is not None and _ts.available()) else "regex"


def _clike_extract(text: str, ext: str):
    """Sound tree-sitter extraction when available, else the conservative regex path.
    Returns (defs, dynamics, file_clean); defs = (name, callees, line, decs, body_ok).
    file_clean=False ⇒ a parse error means enumeration may be incomplete (→ dark file)."""
    if _ts is not None and _ts.available():
        lk = _TS_LANG.get(ext)
        if lk:
            r = _ts.extract(text, lk)
            if r is not None:
                return r                       # (defs, dynamics, file_clean)
    defs, dynamics = _extract_clike(text)      # regex path: per-def body_ok flags truncation
    return defs, dynamics, True


# --------------------------------------------------------------------------- #
# graph
# --------------------------------------------------------------------------- #
class CallGraph:
    def __init__(self) -> None:
        self.defs: dict[str, list[dict]] = {}        # name -> [{file,line,decorators}]
        self.edges: dict[str, set[str]] = {}         # caller -> {callees}
        self._callers: dict[str, set[str]] = {}      # callee -> {callers} (lazy)
        self._built_callers = False
        # --- coverage / blind-spot signals (consumed by prioritise/coverage.py) ---
        self.parse_failures: list[dict] = []         # [{file}] — file the parser could not read at all
        self.parse_incomplete: list[dict] = []       # [{file,name,line}] — body couldn't be bounded (dark)
        self.dynamic_sites: list[dict] = []          # [{file,line,kind,enclosing}]
        self.code_files = 0                          # total source files walked
        self.exported: set[str] = set()              # public-API names — the entry surface

    def add_def(self, name, file, line, decorators):
        self.defs.setdefault(name, []).append(
            {"file": file, "line": line, "decorators": list(decorators or [])})

    def add_edges(self, caller, callees):
        if not callees:
            return
        self.edges.setdefault(caller, set()).update(callees)

    def _ensure_callers(self):
        if self._built_callers:
            return
        for caller, callees in self.edges.items():
            for c in callees:
                self._callers.setdefault(c, set()).add(caller)
        self._built_callers = True

    def defined(self, name: str | None) -> bool:
        return bool(name) and name in self.defs

    def fan_in(self, name: str | None) -> int:
        """Distinct functions that call `name` (excluding self-recursion)."""
        if not name:
            return 0
        self._ensure_callers()
        return len(self._callers.get(name, set()) - {name})

    def reachable_from(self, roots: set[str]) -> set[str]:
        """Forward BFS over caller→callee edges: every symbol transitively called
        from a boundary entrypoint (the roots are included)."""
        seen: set[str] = set()
        stack = [r for r in roots]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            for callee in self.edges.get(cur, ()):
                if callee not in seen:
                    stack.append(callee)
        return seen


def build(base: str, exclude_globs=()) -> CallGraph:
    cg = CallGraph()
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, base)
            if ext not in _PY_EXT and ext not in _CLIKE:
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            cg.code_files += 1
            file_clean = True
            if ext in _PY_EXT:
                defs, top, dynamics, parse_ok = _extract_python(text)
                cg.add_edges(TOPLEVEL, top)
                cg.exported |= _python_public_names(text)
                if not parse_ok:
                    cg.parse_failures.append({"file": rel})
                defs = [(n, c, l, d, True) for (n, c, l, d) in defs]  # ast bodies are reliably bounded
            else:
                defs, dynamics, file_clean = _clike_extract(text, ext)
                cg.exported |= _clike_exported_names(text)
            for name, callees, line, decs, body_ok in defs:
                cg.add_def(name, rel, line, decs)
                if body_ok:
                    cg.add_edges(name, callees)
                else:
                    # CONSERVATIVE: a body we couldn't bound has unreliable callees —
                    # drop them (never falsely mark a target reachable) and flag it dark.
                    cg.parse_incomplete.append({"file": rel, "name": name, "line": line})
            if not file_clean:
                # the file had a parse error → enumeration may be incomplete; record it
                # so a possibly-hidden function is accounted for as dark, not absent.
                cg.parse_incomplete.append({"file": rel, "name": None, "line": 1})
            for d in dynamics:
                cg.dynamic_sites.append({"file": rel, "line": d["line"],
                                         "kind": d["kind"], "enclosing": d["enclosing"]})
    return cg


def boundary_entrypoints(cg: CallGraph, base: str, bcfg: dict) -> set[str]:
    """Def names that sit on a trust boundary: name matches a symbol pattern, or
    the def is decorated with a boundary marker, or it lives in a boundary file.
    `<toplevel>` (module-level code, runs on import) is always an entrypoint."""
    import fnmatch
    roots: set[str] = {TOPLEVEL}
    sym_pats = bcfg.get("symbol_patterns", []) or []
    path_globs = bcfg.get("path_globs", []) or []
    markers = bcfg.get("decorator_markers", []) or []
    for name, sites in cg.defs.items():
        if any(fnmatch.fnmatch(name, p) for p in sym_pats):
            roots.add(name); continue
        for site in sites:
            decs = site.get("decorators", [])
            if any(any(mk.strip("@(").rstrip("(") in d for d in decs) for mk in markers):
                roots.add(name); break
            rel = (site.get("file") or "").replace("\\", "/")
            from sariflib import glob_match_path  # local import; sariflib on path
            if glob_match_path(rel, path_globs):
                roots.add(name); break
    # The PUBLIC API surface is an entry surface too: external callers reach exported
    # / public symbols, so a library (no handler/route/main boundary) isn't 100% dark.
    # Sound — a public symbol is callable from outside by definition. Toggle off with
    # boundary.include_public_api: false.
    if bcfg.get("include_public_api", True):
        roots |= {n for n in cg.exported if n in cg.defs}
    return roots
