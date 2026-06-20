#!/usr/bin/env python3
"""
treesitter_graph.py — SOUND syntactic call-graph extraction for TS/JS/TSX/JSX/Rust.

The regex brace extractor in callgraph.py is conservative best-effort: it can miss
exotic definition shapes (so a function is silently un-enumerated) and mis-handle
braces inside strings/regex literals. This module uses real tree-sitter grammars,
which gives:
  * SOUND enumeration — every definition the grammar knows (declarations, function
    expressions, arrow functions, methods, generators, Rust fn/impl items).
  * reliable bodies — a body is an AST node, not a brace guess (no string/comment/
    regex fragility).
  * precise dynamic-dispatch detection (eval / computed member call / new Function /
    dynamic require).
  * honest errors — a definition whose subtree contains a tree-sitter ERROR/MISSING
    node is reported body_ok=False → callgraph treats it as parse-incomplete (dark)
    and drops its (unreliable) edges. Conservative, now precise.

OPTIONAL: if tree-sitter or a grammar is not installed, `available()` is False and
callgraph.py falls back to the regex extractor. Python stays on stdlib `ast`.

Returns the SAME shape as callgraph._extract_clike:
    (defs, dynamics)
    defs     = [(name, callees:set[str], line:int, decorators:list, body_ok:bool)]
    dynamics = [{"line": int, "kind": str, "enclosing": str}]

Honest ceiling: edges are NAME-based, not type-resolved (`obj.m()` -> callee "m",
not which class's m). Rust macro-generated code is invisible without expansion →
conservatively dark. See GUARANTEES.md.
"""
from __future__ import annotations

TOPLEVEL = "<toplevel>"

# ext/lang key -> grammar loader (lazy). Populated on first use.
_LOADERS = {
    "typescript": ("tree_sitter_typescript", "language_typescript"),
    "tsx":        ("tree_sitter_typescript", "language_tsx"),
    "javascript": ("tree_sitter_javascript", "language"),
    "rust":       ("tree_sitter_rust", "language"),
}
_LANG_CACHE: dict = {}
_TS_CORE = None   # the tree_sitter module, or False if unavailable


def _core():
    global _TS_CORE
    if _TS_CORE is None:
        try:
            import tree_sitter
            _TS_CORE = tree_sitter
        except Exception:
            _TS_CORE = False
    return _TS_CORE


def available() -> bool:
    return bool(_core())


def _get_lang(lang_key: str):
    if lang_key in _LANG_CACHE:
        return _LANG_CACHE[lang_key]
    core = _core()
    spec = _LOADERS.get(lang_key)
    lang = None
    if core and spec:
        mod_name, fn_name = spec
        try:
            mod = __import__(mod_name)
            lang = core.Language(getattr(mod, fn_name)())
        except Exception:
            lang = None
    _LANG_CACHE[lang_key] = lang
    return lang


# node types per family
_DEF_TS = {"function_declaration", "generator_function_declaration",
           "function_expression", "function", "arrow_function", "method_definition"}
_DEF_RUST = {"function_item"}
_NAME_NODE_TYPES = {"identifier", "property_identifier", "type_identifier",
                    "shorthand_property_identifier", "field_identifier"}


def _txt(node) -> str:
    try:
        return node.text.decode("utf-8", "replace")
    except Exception:
        return ""


def _last_component(s: str) -> str:
    # foo.bar.baz -> baz ; a::b::c -> c
    return s.replace("::", ".").split(".")[-1].strip()


def _def_name(node):
    """Best-effort callable name for a definition node (None if anonymous)."""
    nm = node.child_by_field_name("name")
    if nm is not None and nm.type in _NAME_NODE_TYPES:
        return _txt(nm)
    # anonymous arrow / function expression — borrow the name it's bound to
    p = node.parent
    if p is None:
        return None
    if p.type == "variable_declarator":
        n = p.child_by_field_name("name")
        return _txt(n) if n is not None and n.type in _NAME_NODE_TYPES else None
    if p.type == "pair":
        k = p.child_by_field_name("key")
        return _txt(k) if k is not None else None
    if p.type in ("public_field_definition", "field_definition", "property_signature"):
        n = p.child_by_field_name("name")
        return _txt(n) if n is not None else None
    if p.type == "assignment_expression":
        left = p.child_by_field_name("left")
        return _last_component(_txt(left)) if left is not None else None
    return None


def _callee(call_node):
    """Return (dynamic_kind|None, callee_name|None) for a call_expression."""
    fn = call_node.child_by_field_name("function")
    if fn is None:
        return None, None
    t = fn.type
    if t in ("identifier", "shorthand_property_identifier"):
        name = _txt(fn)
        if name == "eval":
            return "eval", "eval"
        if name == "require":
            args = call_node.child_by_field_name("arguments")
            if args is not None and not any(c.type in ("string", "template_string") for c in args.children):
                return "dynamic-require", "require"
        return None, name
    if t in ("member_expression", "field_expression"):
        prop = fn.child_by_field_name("property") or fn.child_by_field_name("field")
        return None, (_txt(prop) if prop is not None else None)
    if t in ("subscript_expression", "index_expression"):
        return "computed-dispatch", None
    if t == "scoped_identifier":                      # rust foo::bar
        return None, _last_component(_txt(fn))
    return None, None                                 # call/parenthesized → returned-callable, dropped


def extract(text: str, lang_key: str):
    """Sound extraction for one clike file. Returns (defs, dynamics) or None if
    tree-sitter / the grammar for lang_key is unavailable."""
    lang = _get_lang(lang_key)
    core = _core()
    if lang is None or not core:
        return None
    try:
        parser = core.Parser(lang)
        tree = parser.parse(bytes(text, "utf-8", "replace"))
    except Exception:
        return None

    def_types = _DEF_RUST if lang_key == "rust" else _DEF_TS
    callees_by_scope: dict = {}     # scope_key -> set[str]
    ok_by_scope: dict = {TOPLEVEL: True}   # scope_key -> body parsed cleanly?
    defrecs = []                    # (scope_key, name, line)
    dynamics = []
    stack = [(tree.root_node, TOPLEVEL, TOPLEVEL)]
    while stack:
        node, scope_key, scope_name = stack.pop()
        # An ERROR or MISSING node anywhere in a function's subtree means we could
        # not reliably parse it → body_ok=False for the enclosing def (conservative
        # dark). MISSING matters: tree-sitter often *recovers* a truncated function
        # by inserting MISSING tokens, leaving has_error False.
        if node.is_error or node.is_missing:
            ok_by_scope[scope_key] = False
        ckey, cname = scope_key, scope_name
        nt = node.type
        if nt in def_types:
            nm = _def_name(node)
            if nm:
                sk = node.id
                callees_by_scope.setdefault(sk, set())
                ok_by_scope.setdefault(sk, True)
                defrecs.append((sk, nm, node.start_point[0] + 1))
                ckey, cname = sk, nm
        elif nt == "call_expression":
            kind, callee = _callee(node)
            if callee:
                callees_by_scope.setdefault(scope_key, set()).add(callee)
            if kind:
                dynamics.append({"line": node.start_point[0] + 1, "kind": kind, "enclosing": scope_name})
        elif nt == "new_expression":
            ctor = node.child_by_field_name("constructor")
            if ctor is not None and _txt(ctor) == "Function":
                dynamics.append({"line": node.start_point[0] + 1, "kind": "function-ctor",
                                 "enclosing": scope_name})
        for c in node.children:
            stack.append((c, ckey, cname))

    defs = [(nm, callees_by_scope.get(sk, set()), line, [], ok_by_scope.get(sk, True))
            for (sk, nm, line) in defrecs]
    # file_clean=False ⇒ the file had a parse error, so enumeration may be INCOMPLETE
    # (a function could be hidden inside an ERROR node, un-enumerated). The caller
    # records the file as parse-incomplete so nothing is silently absent.
    file_clean = not tree.root_node.has_error
    return defs, dynamics, file_clean
