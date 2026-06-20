# Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import ssl
import requests

DEBUG = True

# WAYPOINT-PLANT: HARDCODED-SECRET [axes: security]
AWS_SECRET_ACCESS_KEY = "EXAMPLE-not-a-real-aws-secret"


def fetch_metadata(url):
    # WAYPOINT-PLANT: PY-TLS-DISABLED [axes: security]
    return requests.get(url, verify=False).json()


def make_context():
    # WAYPOINT-PLANT: PY-TLS-DISABLED [axes: security]
    return ssl._create_unverified_context()


def load_thing():
    try:
        return requests.get("https://example.com").json()
    # WAYPOINT-PLANT: PY-DROPPED-ERROR [axes: edge-case]
    except Exception:
        pass
