"""Tests for the fallback dispatcher: envelope, prompt, dry-run, verdict loop."""
import json
import os

import sariflib as S
import fallback_dispatcher as D
import suppress
from conftest import beacon


def test_callees_skips_keywords():
    region = "if cond:\n    cur.execute(sql)\n    return helper(x)\n"
    callees = D.callees_in(region)
    assert "execute" in callees and "helper" in callees
    assert "if" not in callees and "return" not in callees


def test_callers_of_finds_sites(tmp_repo):
    callers = D.callers_of("lookup", str(tmp_repo))
    # two call sites in svc.py caller(); the def line is excluded
    assert any("svc.py:5" in c for c in callers)
    assert all("def lookup" not in c for c in callers)


def test_build_envelope_and_prompt(tmp_repo):
    b = beacon("app.py", 3, 3, axes=["security", "abuse"], hypothesis="injection here?",
             chash="abcd1234")
    b["properties"][S.WP]["rank"] = 1
    b["properties"][S.WP]["score"] = 1.4
    env = D.build_envelope(b, str(tmp_repo), pad=2)
    assert env["symbol"] == "handle_request"
    assert "cache[req] = 1" in env["region_padded"]
    prompt = D.render_prompt(env)
    assert "injection here?" in prompt
    assert "confirm / dismiss / escalate" in prompt
    assert "handle_request" in prompt          # callers section references the symbol


def test_dispatch_dry_run_writes_prompts(tmp_repo):
    base = str(tmp_repo)
    sarif = S.empty_sarif("waypoint-ranked")
    b = beacon("app.py", 3, 3, axes=["security"], chash="hh")
    b["properties"][S.WP]["rank"] = 1
    sarif["runs"][0]["results"] = [b]
    rpath = str(tmp_repo / "ranked.sarif"); S.write_sarif(sarif, rpath)
    out_dir = str(tmp_repo / "dispatch")

    rc = D.main([rpath, "--backend", "dry-run", "--out-dir", out_dir, "--base", base])
    assert rc == 0
    files = os.listdir(out_dir)
    assert any(f.endswith(".md") for f in files)
    manifest = json.load(open(os.path.join(out_dir, "manifest.json")))
    assert manifest[0]["content_hash"] == "hh"
    # dry-run must not produce verdicts
    assert "verdicts.json" not in files


def test_extract_json_ignores_prose_braces():
    # a real verdict must survive prose that itself contains braces (#2)
    v = D._extract_json('I weighed {some options} first.\n'
                        '{"verdict":"dismiss","confidence":0.8}\nDone.')
    assert v["verdict"] == "dismiss" and v["confidence"] == 0.8


def test_dispatch_empty_runs_does_not_crash(tmp_path):
    sarif = {"version": "2.1.0", "runs": []}            # no runs at all (#3)
    rpath = str(tmp_path / "r.sarif"); S.write_sarif(sarif, rpath)
    assert D.main([rpath, "--backend", "dry-run", "--out-dir", str(tmp_path / "d")]) == 0


def test_record_verdicts_writes_dismissals(tmp_path):
    store = str(tmp_path / "store.json")
    verdicts = [
        {"content_hash": "d1", "verdict": "dismiss", "rule_id": "r", "file": "f", "reasoning": "ok"},
        {"content_hash": "c1", "verdict": "confirm", "rule_id": "r", "file": "f"},
    ]
    n = D.record_verdicts(verdicts, store, expiry_days=90)
    assert n == 1                                        # only the dismissal recorded
    s = suppress.load_store(store)
    assert s["suppressions"][0]["content_hash"] == "d1"
    assert s["suppressions"][0]["by"] == "agent"
