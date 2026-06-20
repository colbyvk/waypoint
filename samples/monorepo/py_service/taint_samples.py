"""Taint-flow fixtures — WAYPOINT-PLANT should fire (input reaches sink),
WAYPOINT-OK must not (constant or parametrized/sanitized)."""
import os
import subprocess
import sqlite3

import requests
from flask import request

conn = sqlite3.connect("db")
cur = conn.cursor()


def sql():
    name = request.args.get("name")
    # WAYPOINT-PLANT: waypoint-py-taint-sql
    cur.execute("SELECT * FROM users WHERE name = '" + name + "'")
    # WAYPOINT-OK: parametrized — the query string is a constant, input is bound
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))


def command():
    host = request.args.get("host")
    # WAYPOINT-PLANT: waypoint-py-taint-command
    os.system("ping -c1 " + host)
    # WAYPOINT-OK: constant command
    os.system("uptime")


def path():
    fn = request.args.get("f")
    # WAYPOINT-PLANT: waypoint-py-taint-path
    open(os.path.join("/data", fn))
    # WAYPOINT-OK: constant path
    open("/etc/hostname")


def ssrf():
    url = request.args.get("u")
    # WAYPOINT-PLANT: waypoint-py-taint-ssrf
    requests.get(url)
    # WAYPOINT-OK: constant, internal URL
    requests.get("https://api.internal/health")


def code():
    expr = request.args.get("e")
    # WAYPOINT-PLANT: waypoint-py-taint-code
    eval(expr)
    # WAYPOINT-OK: constant expression
    eval("1 + 1")


def deserialize():
    import pickle
    blob = request.data
    # WAYPOINT-PLANT: waypoint-py-taint-deserialize
    pickle.loads(blob)
    # WAYPOINT-OK: constant bytes
    pickle.loads(b"")


def ssti():
    from flask import render_template_string
    tmpl = request.args.get("t")
    # WAYPOINT-PLANT: waypoint-py-taint-ssti
    render_template_string(tmpl)
    # WAYPOINT-OK: constant template
    render_template_string("<h1>hi</h1>")
