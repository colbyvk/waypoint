"""Tests for deploy_readiness.py bucket/signal classification."""
import deploy_readiness as D


def test_bandit_codes_bucketed_by_severity():
    # serious bandit/ruff codes are ship-stoppers...
    for code in ("S301", "B301", "S608", "B602", "S310", "B501", "S105", "S307", "S314"):
        assert D.bucket(code) == "ship-stopper", code
    # ...lower-impact ones are review, not ship-stopper
    for code in ("S324", "S311", "B113", "S104", "B303"):
        assert D.bucket(code) == "review", code


def test_custom_rules_bucketed():
    for rid in ("waypoint-py-eval-exec", "waypoint-py-taint-sql",
                "waypoint-py-authz-route-no-auth", "waypoint-py-hardcoded-secret",
                "waypoint-ts-cors-wildcard", "waypoint-py-tls-verify-disabled"):
        assert D.bucket(rid) == "ship-stopper", rid
    assert D.bucket("waypoint-ts-insecure-cookie") == "review"
    assert D.bucket("waypoint-py-logic-self-comparison") == "info"
    assert D.bucket("F401") == "info"  # an unused-import lint is not a deploy risk


def test_signal_labels():
    assert D._signal("waypoint-py-hardcoded-secret") == "secrets"
    assert D._signal("S105") == "secrets"
    assert D._signal("waypoint-py-authz-route-no-auth") == "auth"
    assert D._signal("waypoint-py-flask-cors-wildcard") == "exposure"
    assert D._signal("waypoint-py-taint-sql") == "injection"


def test_bucket_handles_empty_and_none():
    assert D.bucket("") == "info"
    assert D.bucket(None) == "info"
