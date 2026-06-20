"""Tests for the shared SARIF library."""
import os

import sariflib as S


def test_content_hash_is_whitespace_insensitive(tmp_repo):
    res = {"locations": [S.physical_location("app.py", 1, 4)]}
    h1 = S.content_hash(str(tmp_repo), res)
    # reindent the same 4 lines: same tokens, must hash the same (a suppression
    # survives cosmetic reflow).
    (tmp_repo / "app.py").write_text(
        "def handle_request(req):\n"
        "        cache = {}\n"
        "        cache[req] = 1\n"
        "        return lookup(req)\n",
        encoding="utf-8",
    )
    h2 = S.content_hash(str(tmp_repo), res)
    assert h1 == h2


def test_content_hash_changes_on_real_edit(tmp_repo):
    res = {"locations": [S.physical_location("app.py", 1, 4)]}
    h1 = S.content_hash(str(tmp_repo), res)
    (tmp_repo / "app.py").write_text(
        "def handle_request(req):\n"
        "    cache = {}\n"
        "    cache[req] = 2\n"            # changed token 1 -> 2
        "    return lookup(req)\n",
        encoding="utf-8",
    )
    h2 = S.content_hash(str(tmp_repo), res)
    assert h1 != h2


def test_content_hash_fallback_when_no_file(tmp_path):
    res = S.make_result("CVE-1", "warning", "vuln", "requirements.txt", 1)
    h = S.content_hash(str(tmp_path), res)
    assert h.startswith("fallback:")          # no readable region -> stable fallback


def test_severity_prior_precedence(tmp_repo):
    cfg = {"severity_prior_map": {"error": 0.9, "warning": 0.6, "note": 0.3, "none": 0.1}}
    # security-severity property (CVSS/10) beats the level map
    r = S.make_result("x", "note", "m", "app.py", 1, properties={"security-severity": "8.0"})
    assert abs(S.severity_prior(r, {}, cfg) - 0.8) < 1e-9
    # otherwise the level map applies
    r2 = S.make_result("x", "error", "m", "app.py", 1)
    assert S.severity_prior(r2, {}, cfg) == 0.9


def test_severity_prior_from_result_property(tmp_repo):
    cfg = {"severity_prior_map": {"warning": 0.6}}
    r = S.make_result("x", "warning", "m", "app.py", 1,
                      properties={"waypoint_severity_prior": 0.95})
    assert S.severity_prior(r, {}, cfg) == 0.95        # explicit prior wins (#8)


def test_severity_prior_tolerates_malformed_properties(tmp_repo):
    cfg = {"severity_prior_map": {"warning": 0.6}}
    r = S.make_result("x", "warning", "m", "app.py", 1)
    r["properties"] = ["bad"]                          # not a dict
    assert S.severity_prior(r, {}, cfg) == 0.6         # falls back, no crash


def test_enclosing_symbol(tmp_repo):
    loc = {"uri": "app.py", "start_line": 3, "end_line": 3}
    assert S.enclosing_symbol(str(tmp_repo), loc) == "handle_request"


def test_validate_sarif_catches_problems():
    bad = {"version": "2.1.0", "runs": [{"tool": {"driver": {}}, "results": [{"ruleId": "x"}]}]}
    errs = S.validate_sarif(bad)
    assert any("driver.name" in e for e in errs)
    assert any("message" in e for e in errs)


def test_strip_uri_handles_file_and_srcroot():
    assert S._strip_uri("file:///a/b.py") == "/a/b.py"
    assert S._strip_uri("%SRCROOT%/a/b.py") == "a/b.py"


def test_resolve_path_clamps_to_base(tmp_path):
    base = str(tmp_path)
    (tmp_path / "in.py").write_text("x", encoding="utf-8")
    assert S.resolve_path("in.py", base).endswith("in.py")       # inside the tree -> ok
    assert S.resolve_path("../../../etc/passwd", base) is None    # traversal escapes -> None
    # a symlink inside the tree pointing OUT of it is also refused
    outside = tmp_path.parent / "wp_secret.txt"; outside.write_text("s", encoding="utf-8")
    try:
        os.symlink(str(outside), str(tmp_path / "link.py"))
    except (OSError, NotImplementedError):
        outside.unlink(missing_ok=True); return                  # platform w/o symlinks
    assert S.resolve_path("link.py", base) is None
    outside.unlink(missing_ok=True)
