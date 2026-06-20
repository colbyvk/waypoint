# Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import os
import re
import subprocess

BASE_DIR = "/var/data"


def ping(host):
    # WAYPOINT-PLANT: PY-SUBPROCESS-SHELL [axes: security]
    return subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)


def read_user_file(user_supplied):
    # WAYPOINT-PLANT: PY-PATH-TRAVERSAL [axes: security]
    with open(os.path.join(BASE_DIR, user_supplied)) as f:
        return f.read()


def read_safe_file(name):
    # WAYPOINT-OK: with-open context manager on a fixed path
    with open(os.path.join(BASE_DIR, "config.json")) as f:
        return f.read()


def parse_int(s):
    try:
        return int(s)
    # WAYPOINT-PLANT: PY-BARE-EXCEPT-PASS [axes: edge-case]
    except:
        pass


def validate(token):
    # WAYPOINT-PLANT: PY-REDOS [axes: abuse,security]
    pattern = re.compile(r"(a+)+$")
    return pattern.match(token)


def count_down(n):
    if n <= 0:
        return 0
    # WAYPOINT-PLANT: PY-INPUT-RECURSION [axes: abuse]
    return count_down(n - 1)
