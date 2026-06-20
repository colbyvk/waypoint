# Intentionally hazardous sample code -- Waypoint hardening2 test fixture.
# Do not deploy. Each `# WAYPOINT-PLANT: <rule-id>` comment precedes a line that
# should fire that rule; `# WAYPOINT-OK:` lines are safe counterparts that should
# NOT fire. The file only needs to parse and be scannable.
import bz2
import gzip
import lzma
import os
import tempfile
import threading
import xml.dom.minidom
import zipfile
import zlib

import jwt
import ldap
import yaml  # noqa
from flask import Flask
from flask_cors import CORS
from django.views.decorators.csrf import csrf_exempt

app = Flask(__name__)


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------

def make_temp():
    # WAYPOINT-PLANT: waypoint-py-insecure-tempfile-mktemp
    path = tempfile.mktemp()
    with open(path, "w") as f:
        f.write("data")
    return path


def make_temp_safe():
    # WAYPOINT-OK: mkstemp creates the file atomically
    fd, path = tempfile.mkstemp()
    return path


@csrf_exempt
def payment_view(request):
    # WAYPOINT-PLANT: waypoint-py-django-csrf-exempt
    return request


def enable_cors_wildcard(application):
    # WAYPOINT-PLANT: waypoint-py-flask-cors-wildcard
    return CORS(application, origins="*")


def enable_cors_resources(application):
    # WAYPOINT-PLANT: waypoint-py-flask-cors-wildcard
    return CORS(application, resources={r"/api/*": {"origins": "*"}})


def enable_cors_safe(application):
    # WAYPOINT-OK: explicit trusted origin
    return CORS(application, origins="https://app.example.com")


def decode_token_noverify(token, key):
    # WAYPOINT-PLANT: waypoint-py-jwt-verify-disabled
    return jwt.decode(token, key, verify=False)


def decode_token_noverify_opts(token, key):
    # WAYPOINT-PLANT: waypoint-py-jwt-verify-disabled
    return jwt.decode(token, key, options={"verify_signature": False})


def decode_token_safe(token, key):
    # WAYPOINT-OK: signature verified with a fixed algorithm
    return jwt.decode(token, key, algorithms=["HS256"])


def ldap_lookup(conn, username):
    # WAYPOINT-PLANT: waypoint-py-ldap-filter-fstring
    return conn.search("dc=example,dc=com", ldap.SCOPE_SUBTREE, f"(uid={username})")


def ldap_lookup_format(conn, username):
    # WAYPOINT-PLANT: waypoint-py-ldap-filter-fstring
    return conn.search("dc=example,dc=com", ldap.SCOPE_SUBTREE, "(uid=%s)" % username)


# ---------------------------------------------------------------------------
# EDGE-CASE
# ---------------------------------------------------------------------------

def read_if_exists(path):
    # WAYPOINT-PLANT: waypoint-py-toctou-exists-open
    if os.path.exists(path):
        f = open(path)
        return f.read()
    return None


def read_if_isfile(path):
    # WAYPOINT-PLANT: waypoint-py-toctou-exists-open
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    return None


def read_direct(path):
    # WAYPOINT-OK: opens directly and handles the error, no check-then-use gap
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None


def parse_int(text):
    # WAYPOINT-PLANT: waypoint-py-reraise-loses-context
    try:
        return int(text)
    except ValueError:
        raise RuntimeError("bad input")


def parse_int_chained(text):
    # WAYPOINT-OK: preserves the original cause with `from`
    try:
        return int(text)
    except ValueError as e:
        raise RuntimeError("bad input") from e


# ---------------------------------------------------------------------------
# CONCURRENCY
# ---------------------------------------------------------------------------

HIT_COUNTS = {}
RESULTS = []


def record_hit(key):
    # WAYPOINT-PLANT: waypoint-py-thread-shared-mutable-nolock
    HIT_COUNTS[key] = HIT_COUNTS.get(key, 0) + 1


def append_result(value):
    # WAYPOINT-PLANT: waypoint-py-thread-shared-mutable-nolock
    RESULTS.append(value)


_LOCK = threading.Lock()


def record_hit_safe(key):
    # WAYPOINT-OK: mutation guarded by a lock
    with _LOCK:
        HIT_COUNTS[key] = HIT_COUNTS.get(key, 0) + 1


def spawn_workers():
    for i in range(10):
        threading.Thread(target=record_hit, args=("k",)).start()


# ---------------------------------------------------------------------------
# ABUSE
# ---------------------------------------------------------------------------

def parse_xml_minidom(xml_text):
    # WAYPOINT-PLANT: waypoint-py-minidom-entity-expansion
    return xml.dom.minidom.parseString(xml_text)


def decompress_zlib(blob):
    # WAYPOINT-PLANT: waypoint-py-decompression-bomb
    return zlib.decompress(blob)


def decompress_gzip(blob):
    # WAYPOINT-PLANT: waypoint-py-decompression-bomb
    return gzip.decompress(blob)


def read_zip_member(path, name):
    # WAYPOINT-PLANT: waypoint-py-decompression-bomb
    return zipfile.ZipFile(path).read(name)


def decompress_bounded(blob):
    # WAYPOINT-OK: decompressor object with a max_length cap (no bare decompress)
    d = zlib.decompressobj()
    return d.decompress(blob, 1024 * 1024)
