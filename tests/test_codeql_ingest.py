"""Verify Waypoint ingests CodeQL SARIF correctly — a cross-file taint result
becomes a security beacon — even before the CodeQL CLI is installed. This banks
the ingestion path so the only thing pending for the deep tier is the CLI itself."""
import os

import sariflib as S
import merge_sarif as MG

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "codeql", "codeql_dataflow.sarif")
TAGMAP = S.load_yaml(os.path.join(S.repo_root(), "tag_map.yaml"))


def test_codeql_sql_dataflow_becomes_security_abuse_beacon():
    sarif = S.read_sarif(FIX)
    run = sarif["runs"][0]
    beacon = MG.normalize_one(run, run["results"][0], S.load_config(), TAGMAP, S.repo_root())
    w = beacon["properties"][S.WP]
    assert set(w["axes"]) == {"security", "abuse"}      # tag_map: codeql *sql* rule
    assert "sql" in w["hypothesis"].lower()
    assert w["tool"] == "CodeQL"
    loc = S.result_location(beacon)
    assert loc["uri"].endswith("queries.py") and loc["start_line"] == 42


def test_codeql_crossfile_path_is_present():
    # the cross-file path (codeFlows) is the whole point — source in routes/api.py
    # reaching a sink in db/queries.py, which per-file scanners can't connect
    result = S.read_sarif(FIX)["runs"][0]["results"][0]
    uris = [l["location"]["physicalLocation"]["artifactLocation"]["uri"]
            for l in result["codeFlows"][0]["threadFlows"][0]["locations"]]
    assert any("routes/api.py" in u for u in uris)      # SOURCE file
    assert any("db/queries.py" in u for u in uris)       # SINK file (different file!)


def test_codeql_severity_prior_from_cvss():
    sarif = S.read_sarif(FIX)
    run = sarif["runs"][0]
    prior = S.severity_prior(run["results"][0], run, S.load_config())
    assert prior > 0.8        # security-severity 8.8 -> ~0.88 prior (ranks high)
