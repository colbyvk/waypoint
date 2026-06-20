"""Tests for the logic-lane normalizers (mutants / race / fuzz -> SARIF beacons)."""
import json
import os
import sys

import sariflib as S

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "detectors", "normalize"))
import mutants_to_sarif as M     # noqa: E402
import race_to_sarif as R        # noqa: E402
import fuzz_to_sarif as F        # noqa: E402
import hypothesis_to_sarif as H  # noqa: E402
import proptest_to_sarif as P    # noqa: E402
import fastcheck_to_sarif as FC  # noqa: E402
import merge_sarif as MG         # noqa: E402  (detectors/ is on sys.path via conftest)

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "logic")


def _read(name):
    return open(os.path.join(FIX, name), encoding="utf-8").read()


def test_mutants_only_surviving_become_beacons():
    data = json.loads(_read("mutants_outcomes.json"))
    res = M.convert(data)["runs"][0]["results"]
    assert len(res) == 2                      # MissedMutant + Timeout; CaughtMutant skipped
    locs = {(S.result_location(r)["uri"], S.result_location(r)["start_line"]) for r in res}
    assert ("src/state.rs", 42) in locs and ("src/exec.rs", 18) in locs
    assert all(r["properties"]["waypoint_axes"] == ["logic"] for r in res)


def test_race_locates_first_source_line():
    res = R.convert(_read("race.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("counter.go") and loc["start_line"] == 15
    assert set(res[0]["properties"]["waypoint_axes"]) == {"logic", "concurrency"}


def test_fuzz_extracts_panic_site_and_message():
    res = F.convert(_read("fuzz_crash.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("parse.rs") and loc["start_line"] == 88
    assert "out of bounds" in S.result_message(res[0])
    assert set(res[0]["properties"]["waypoint_axes"]) == {"logic", "edge-case"}


def test_clean_output_yields_no_beacons():
    assert F.convert("all good, no crash here")["runs"][0]["results"] == []
    assert R.convert("no races detected")["runs"][0]["results"] == []
    assert M.convert({"outcomes": []})["runs"][0]["results"] == []


def test_logic_is_a_registered_axis():
    assert "logic" in S.AXES


# --------------------------------------------------------------------------- #
# property-based testing — a counterexample becomes a logic beacon that carries
# the MINIMAL reproducing input (the actionability a static beacon can't give).
# --------------------------------------------------------------------------- #
def test_hypothesis_blames_source_and_captures_repro():
    res = H.convert(_read("hypothesis_falsifying.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    # the buggy source frame, NOT the test_ file
    assert loc["uri"].endswith("clamp.py") and loc["start_line"] == 14
    props = res[0]["properties"]
    assert "x=0" in props["waypoint_reproducing_input"]
    assert props["waypoint_property"]                       # the violated assertion
    assert set(props["waypoint_axes"]) == {"logic", "edge-case"}


def test_proptest_blames_source_and_captures_repro():
    res = P.convert(_read("proptest_failure.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("math.rs") and loc["start_line"] == 23
    assert "x = 0" in res[0]["properties"]["waypoint_reproducing_input"]
    assert set(res[0]["properties"]["waypoint_axes"]) == {"logic", "edge-case"}


def test_fastcheck_blames_user_frame_not_the_test():
    res = FC.convert(_read("fastcheck_failure.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("util.ts") and not loc["uri"].endswith("util.test.ts")
    assert loc["start_line"] == 7
    assert res[0]["properties"]["waypoint_reproducing_input"] == "[0,0,-1]"
    assert set(res[0]["properties"]["waypoint_axes"]) == {"logic", "edge-case"}


# --------------------------------------------------------------------------- #
# fuzzing — now four-language (Rust panic, Python/atheris, JS/jazzer), and each
# crash carries the crashing input (libFuzzer Base64 / saved artifact).
# --------------------------------------------------------------------------- #
def test_fuzz_atheris_python_crash_blames_code_not_harness():
    res = F.convert(_read("atheris_crash.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("money.py") and loc["start_line"] == 19
    assert "invalid literal" in S.result_message(res[0])
    assert "AA==" in res[0]["properties"]["waypoint_reproducing_input"]
    assert set(res[0]["properties"]["waypoint_axes"]) == {"logic", "edge-case"}


def test_fuzz_jazzer_js_crash():
    res = F.convert(_read("jazzer_crash.txt"))["runs"][0]["results"]
    assert len(res) == 1
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("money.ts") and loc["start_line"] == 14
    assert "must be positive" in S.result_message(res[0])
    assert "LTE=" in res[0]["properties"]["waypoint_reproducing_input"]


def test_property_clean_output_yields_no_beacons():
    assert H.convert("1 passed in 0.01s")["runs"][0]["results"] == []
    assert P.convert("test result: ok. 3 passed; 0 failed")["runs"][0]["results"] == []
    assert FC.convert("Tests  3 passed (3)")["runs"][0]["results"] == []


def test_metamorphic_relation_is_subtagged():
    """A falsified roundtrip (decode∘encode == id) — the strongest spec-free
    property — is labelled with its relation kind, so it's recognizable as
    differential/metamorphic evidence rather than a generic property failure."""
    res = H.convert(_read("hypothesis_roundtrip.txt"))["runs"][0]["results"]
    assert len(res) == 1
    p = res[0]["properties"]
    assert "roundtrip" in p.get("waypoint_subtags", [])
    loc = S.result_location(res[0])
    assert loc["uri"].endswith("serializer.py") and loc["start_line"] == 22
    assert "data=" in p["waypoint_reproducing_input"]


def test_relation_subtags_helper():
    assert "roundtrip" in S.property_relation_subtags("test_roundtrip: decode(encode(x))")
    assert "idempotent" in S.property_relation_subtags("normalize is idempotent")
    assert "differential" in S.property_relation_subtags("equivalent to reference_impl")
    assert S.property_relation_subtags("just a plain assertion x < y") == []


def test_reproducing_input_survives_merge_into_beacon():
    """The whole point: the repro must reach the beacon. Run a property failure
    through merge_sarif.normalize_one and confirm the nested waypoint block keeps
    the reproducing input + violated property."""
    raw = H.convert(_read("hypothesis_falsifying.txt"))
    run = raw["runs"][0]
    beacon = MG.normalize_one(run, run["results"][0], S.load_config(), {}, S.repo_root())
    w = beacon["properties"][S.WP]
    assert "x=0" in w["reproducing_input"]
    assert w["property"]
    assert set(w["axes"]) == {"edge-case", "logic"}
