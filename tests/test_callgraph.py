"""Tests for the real call graph (centrality fan-in + proven reachability)."""
import callgraph as CG

PY = """
def handle_request(req):       # boundary entrypoint (matches handle_*)
    return service(req)

def service(x):
    return helper(x) + helper(x)

def helper(y):
    return y

def _unused():                 # PRIVATE, defined but never called -> dark
    return 0
"""


def _build(tmp_path, files):
    for name, txt in files.items():
        (tmp_path / name).write_text(txt, encoding="utf-8")
    return CG.build(str(tmp_path))


def test_python_fan_in_counts_distinct_callers(tmp_path):
    cg = _build(tmp_path, {"app.py": PY})
    assert cg.defined("helper")
    assert cg.fan_in("helper") == 1     # service calls it twice -> 1 DISTINCT caller
    assert cg.fan_in("service") == 1     # handle_request
    assert cg.fan_in("_unused") == 0


def test_python_reachability_from_boundary(tmp_path):
    cg = _build(tmp_path, {"app.py": PY})
    bcfg = {"symbol_patterns": ["handle_*"], "path_globs": [], "decorator_markers": []}
    roots = CG.boundary_entrypoints(cg, str(tmp_path), bcfg)
    reach = cg.reachable_from(roots)
    assert "handle_request" in roots
    assert {"handle_request", "service", "helper"} <= reach   # transitively reachable
    assert "_unused" not in reach                             # private + uncalled -> dark


def test_public_api_is_an_entrypoint_surface(tmp_path):
    # a library with no handler/route/main boundary: its PUBLIC API is the entry
    # surface, so public symbols seed reachability — otherwise everything reads
    # 100% dark (the `ky` problem). Private + uncalled code stays dark.
    lib = ("def public_fn(x):\n"
           "    return _helper(x)\n\n"
           "def _helper(y):\n"
           "    return y\n\n"
           "def _dead():\n"
           "    return 0\n\n"
           "class PublicThing:\n"
           "    def method(self):\n"
           "        return _helper(1)\n")
    cg = _build(tmp_path, {"lib.py": lib})
    roots = CG.boundary_entrypoints(cg, str(tmp_path), {})    # no boundary config => library
    reach = cg.reachable_from(roots)
    assert "public_fn" in roots and "method" in roots         # public func + public method = entry
    assert "_helper" in reach                                  # reached via the public API
    assert "_dead" not in reach                               # private + uncalled -> still dark


def test_public_api_seeding_can_be_disabled(tmp_path):
    cg = _build(tmp_path, {"lib.py": "def public_fn(x):\n    return 1\n"})
    roots = CG.boundary_entrypoints(cg, str(tmp_path), {"include_public_api": False})
    assert "public_fn" not in roots                           # opted out -> not an entry


def test_decorator_marks_entrypoint(tmp_path):
    src = ("import flask\n"
           "@app.route('/x')\n"
           "def view():\n"
           "    return work()\n\n"
           "def work():\n"
           "    return 1\n")
    cg = _build(tmp_path, {"v.py": src})
    bcfg = {"symbol_patterns": [], "path_globs": [], "decorator_markers": ["@app.route"]}
    roots = CG.boundary_entrypoints(cg, str(tmp_path), bcfg)
    assert "view" in roots
    assert "work" in cg.reachable_from(roots)        # reached only via the call edge


def test_clike_extracts_real_edges(tmp_path):
    ts = ("function outer(){ return inner(); }\n"
          "function inner(){ return leaf(); }\n"
          "function leaf(){ return 1; }\n")
    cg = _build(tmp_path, {"a.ts": ts})
    assert cg.defined("inner") and cg.fan_in("inner") == 1
    assert {"outer", "inner", "leaf"} <= cg.reachable_from({"outer"})


def test_clike_export_and_rust_pub_seed_entrypoints(tmp_path):
    ts = ("export function api(){ return impl(); }\n"
          "function impl(){ return 1; }\n"
          "function unused(){ return 2; }\n")
    cg = _build(tmp_path, {"a.ts": ts})
    reach = cg.reachable_from(CG.boundary_entrypoints(cg, str(tmp_path), {}))
    assert "api" in reach and "impl" in reach     # exported entry + its callee
    assert "unused" not in reach                  # not exported, not called -> dark
    rs = ("pub fn api() -> i32 { helper() }\nfn helper() -> i32 { 1 }\nfn dead() -> i32 { 2 }\n")
    cg2 = _build(tmp_path, {"b.rs": rs})
    reach2 = cg2.reachable_from(CG.boundary_entrypoints(cg2, str(tmp_path), {}))
    assert "api" in reach2 and "helper" in reach2  # pub fn entry + callee
    assert "dead" not in reach2                     # private rust fn, uncalled -> dark


def test_unparseable_file_does_not_crash(tmp_path):
    cg = _build(tmp_path, {"broken.py": "def (((\n"})
    assert cg.fan_in("anything") == 0      # syntax error -> empty graph, no crash


def test_clike_brace_matcher_is_string_and_comment_aware(tmp_path):
    # braces inside a string / comment must NOT break body-bounding — otherwise the
    # matcher mis-bounds and would trust WRONG callees (an unsound false edge).
    src = ('function outer() {\n'
           '  const s = "a { brace } in a string";  // and a } in a comment\n'
           '  /* a { block } comment */\n'
           '  return inner();\n'
           '}\n'
           'function inner() { return 1; }\n')
    cg = _build(tmp_path, {"a.ts": src})
    assert cg.fan_in("inner") == 1                       # edge survived the brace noise
    assert {"outer", "inner"} <= cg.reachable_from({"outer"})
    assert not cg.parse_incomplete                       # bounded cleanly, not flagged dark


def test_clike_unbounded_body_is_conservatively_dark(tmp_path):
    # a truncated function is recorded DARK and its (unreliable) callees DROPPED —
    # never used to mark a target reachable. Regex flags it by name; tree-sitter
    # flags the file (the function hides inside an ERROR node). Either is conservative.
    cg = _build(tmp_path, {"a.ts": "function leaky() {\n  reach_me(\n"})
    assert cg.parse_incomplete                           # recorded dark (by-name OR file-level)
    assert cg.fan_in("reach_me") == 0                    # dropped edge — never falsely reachable


def test_clike_falls_back_to_regex_without_treesitter(tmp_path, monkeypatch):
    # the regex extractor must keep working when tree-sitter isn't installed.
    import callgraph as CG
    monkeypatch.setattr(CG, "_ts", None)
    assert CG.clike_backend() == "regex"
    cg = _build(tmp_path, {"a.ts": "function a(){ return b(); }\nfunction b(){ return 1; }\n"})
    assert cg.fan_in("b") == 1                            # regex path still extracts edges
