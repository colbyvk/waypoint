"""Tests for the coverage / blind-spot map (the "dark zone").

Two properties under test: (1) HONESTY — gaps are tiered by OBSERVED facts, never a
float severity, and un-traversed regions are graded nothing; (2) the COVERAGE
PARTITION — analyzed ∪ dark = all enumerated functions, with a conservative graph.
Waypoint's own Python only; tiny temp trees; no external scanner.
"""
import coverage as COV


def _cfg():
    return {
        "boundary": {"symbol_patterns": ["handle_*", "*_view", "main"],
                     "path_globs": ["**/handlers/**", "**/app.py"],
                     "decorator_markers": ["@app.route"]},
        "coverage": {"top_k": 25},
    }


def _gather(tmp_path, files):
    for name, txt in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")
    return COV.gather(str(tmp_path), _cfg())


def _by_name(rep, name):
    return next(g for g in rep["gaps"] if g.get("name") == name)


# --- honesty: tiers from observed facts, NO float severity --------------------
def test_no_gap_carries_a_float_severity(tmp_path):
    rep = _gather(tmp_path, {"a.py": "import subprocess\ndef r(c):\n    return subprocess.run(c)\n"})
    assert rep["gaps"]
    for g in rep["gaps"]:
        assert "relevance" not in g and "score" not in g
        assert g["reachability"] == "unresolved"


def test_exec_is_code_exec_tier(tmp_path):
    rep = _gather(tmp_path, {"a.py": "def f(code):\n    exec(code)\n"})
    g = next(g for g in rep["gaps"] if g["kind"] == "dynamic-dispatch" and g["line"] == 2)
    assert g["tier"] == "code-exec-adjacent"
    assert g["observed"]["dynamic_kind"] == "exec"


def test_getattr_literal_static_but_computed_dynamic(tmp_path):
    rep = _gather(tmp_path, {"a.py":
        "def f(o, n):\n    a = getattr(o, 'name', None)\n    b = getattr(o, n)\n"})
    lines = {g["line"] for g in rep["gaps"] if g["kind"] == "dynamic-dispatch"}
    assert 3 in lines and 2 not in lines


def test_orphan_reaching_io_sink_is_sink_tier(tmp_path):
    rep = _gather(tmp_path, {"h.py": "import requests\ndef fetch(u):\n    return requests.get(u)\n"})
    g = _by_name(rep, "fetch")
    assert g["tier"] == "sink-adjacent" and "get" in g["observed"]["sinks"]


def test_orphan_reaching_code_exec_sink_is_code_exec_tier(tmp_path):
    rep = _gather(tmp_path, {"h.py": "import subprocess\ndef run_it(c):\n    return subprocess.run(c)\n"})
    g = _by_name(rep, "run_it")
    assert g["tier"] == "code-exec-adjacent" and "run" in g["observed"]["sinks"]


def test_bare_orphan_is_opaque(tmp_path):
    rep = _gather(tmp_path, {"u.py": "def util():\n    return 1 + 1\n"})
    assert _by_name(rep, "util")["tier"] == "opaque"


def test_code_exec_orders_before_io_sink(tmp_path):
    rep = _gather(tmp_path, {
        "a.py": "import subprocess\ndef run_it(c):\n    return subprocess.run(c)\n",
        "b.py": "import requests\ndef fetch(u):\n    return requests.get(u)\n"})
    order = [g.get("name") for g in rep["gaps"] if g.get("name") in ("run_it", "fetch")]
    assert order.index("run_it") < order.index("fetch")   # gaps pre-sorted: code-exec first


def test_demo_path_is_a_hint_and_sorts_after(tmp_path):
    rep = _gather(tmp_path, {
        "src/h.py": "import subprocess\ndef run_a(c):\n    return subprocess.run(c)\n",
        "examples/h.py": "import subprocess\ndef run_b(c):\n    return subprocess.run(c)\n"})
    names = [g.get("name") for g in rep["gaps"] if g.get("name") in ("run_a", "run_b")]
    assert names.index("run_a") < names.index("run_b")
    assert "example/demo path" in _by_name(rep, "run_b")["hints"]


def test_test_and_vendor_paths_excluded(tmp_path):
    rep = _gather(tmp_path, {"tests/test_x.py": "def test_t():\n    exec('1')\n",
                             "node_modules/x.py": "def f(c):\n    exec(c)\n"})
    assert all("test" not in g["file"] and "node_modules" not in g["file"] for g in rep["gaps"])


def test_unparsed_file_is_graded_nothing(tmp_path):
    rep = _gather(tmp_path, {"broken.py": "def f(:\n    pass\n"})
    g = next(g for g in rep["gaps"] if g["kind"] == "unparsed-file")
    assert g["tier"] == "unparsed" and g["observed"]["parsed"] is False


# --- the partition guarantee (Phase B) ---------------------------------------
def test_partition_holds_and_accounts_for_all(tmp_path):
    rep = _gather(tmp_path, {"app.py":
        "def main():\n    return work()\n"
        "def work():\n    return 1\n"
        "def stray():\n    return 2\n"})
    s = rep["summary"]
    assert s["partition_holds"] is True
    assert s["analyzed"] + s["dark"] == s["functions"]


def test_conservative_dynamic_only_reach_stays_dark(tmp_path):
    # `target` is reachable ONLY via a computed getattr dispatch → must never be
    # counted analyzed (erring dark is the soundness direction).
    # lib.py is NOT a boundary file, so only `main` (symbol-pattern entrypoint) is a
    # root; `target` is reachable only via the unresolved getattr dispatch.
    rep = _gather(tmp_path, {"lib.py":
        "def main(n, x):\n    return getattr(x, n)()\n"   # computed dispatch — edge unresolved
        "def target():\n    return 1\n"})
    assert rep["summary"]["partition_holds"]
    # target has no resolved caller → it must be DARK (an orphan gap), never analyzed
    assert _by_name(rep, "target")["tier"] in ("opaque", "sink-adjacent", "code-exec-adjacent")
    assert rep["summary"]["analyzed"] == 1   # only main is entrypoint-reachable; target stays dark


def test_clike_unbounded_brace_is_parse_incomplete(tmp_path):
    # a TS function whose brace never closes → conservatively dark, edges dropped
    rep = _gather(tmp_path, {"a.ts": "function leaky() {\n    doThing(\n"})
    assert rep["summary"]["partition_holds"]
    assert any(g["kind"] == "parse-incomplete" for g in rep["gaps"])


def test_summary_shape(tmp_path):
    rep = _gather(tmp_path, {"app.py": "def main():\n    return work()\ndef work():\n    return 1\n"})
    s = rep["summary"]
    for k in ("functions", "analyzed", "dark", "partition_holds", "tiers", "graph_traceability_pct"):
        assert k in s


# --- investigate envelope (the LLM dark-zone prompt) -------------------------
def test_gap_envelope_and_prompt(tmp_path):
    import fallback_dispatcher as FD
    (tmp_path / "a.py").write_text("def f(code):\n    exec(code)\n", encoding="utf-8")
    gap = {"file": "a.py", "line": 2, "kind": "dynamic-dispatch", "name": None,
           "enclosing": "f", "tier": "code-exec-adjacent",
           "observed": {"sinks": ["exec"], "dynamic_kind": "exec"},
           "reachability": "unresolved", "reasons": ["observed: computed `exec` dispatch"],
           "hypothesis": "Trace whether input reaches exec."}
    env = FD.build_gap_envelope(gap, str(tmp_path), pad=3)
    assert env["content_hash"] and len(env["content_hash"]) == 24
    prompt = FD.render_gap_prompt(env)
    assert "exec" in prompt and "could not be verified" in prompt.lower()
