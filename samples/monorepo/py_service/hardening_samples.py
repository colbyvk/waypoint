# Intentionally insecure sample code -- Waypoint hardening test fixture. Do not deploy.
# Each `# WAYPOINT-PLANT: <rule-id>` comment precedes a line that should fire that
# rule; adjacent `# WAYPOINT-OK:` lines are safe counterparts that should NOT fire.
# Imports may be unused; the file only needs to parse (ast.parse) and be scannable.
import asyncio
import hashlib
import marshal
import os
import pickle
import random
import ssl
import tarfile
import time
import xml.etree.ElementTree as ET
import zipfile

import httpx
import requests
import urllib.request
import yaml
from Crypto.Cipher import AES
from flask import Flask, render_template_string, request
from jinja2 import Environment
from django.utils.safestring import mark_safe
import lxml.etree

app = Flask(__name__)


# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------

def deserialize_pickle(blob):
    # WAYPOINT-PLANT: waypoint-py-unsafe-deser
    return pickle.loads(blob)


def deserialize_pickle_file(fp):
    # WAYPOINT-PLANT: waypoint-py-unsafe-deser
    return pickle.load(fp)


def deserialize_marshal(blob):
    # WAYPOINT-PLANT: waypoint-py-unsafe-deser
    return marshal.loads(blob)


def load_yaml_unsafe(text):
    # WAYPOINT-PLANT: waypoint-py-yaml-unsafe-load
    return yaml.load(text)


def load_yaml_unsafe_fullloader(text):
    # WAYPOINT-PLANT: waypoint-py-yaml-unsafe-load
    return yaml.load(text, Loader=yaml.FullLoader)


def load_yaml_safe(text):
    # WAYPOINT-OK: SafeLoader is used
    return yaml.load(text, Loader=yaml.SafeLoader)


@app.route("/render")
def render_dynamic():
    tmpl = request.args.get("tmpl", "")
    # WAYPOINT-PLANT: waypoint-py-ssti-render-template-string
    return render_template_string(tmpl)


def render_constant():
    # WAYPOINT-OK: literal template, no injection surface
    return render_template_string("<h1>hello</h1>")


def jinja_no_autoescape():
    # WAYPOINT-PLANT: waypoint-py-jinja-autoescape-off
    return Environment(autoescape=False)


def jinja_autoescape_on():
    # WAYPOINT-OK: autoescape enabled
    return Environment(autoescape=True)


def render_mark_safe(user_html):
    # WAYPOINT-PLANT: waypoint-py-django-mark-safe
    return mark_safe(user_html)


def fetch_remote(url):
    # WAYPOINT-PLANT: waypoint-py-ssrf-nonliteral-url
    return requests.get(url, timeout=5).text


def fetch_remote_urllib(url):
    # WAYPOINT-PLANT: waypoint-py-ssrf-nonliteral-url
    return urllib.request.urlopen(url)


def fetch_remote_httpx(url):
    # WAYPOINT-PLANT: waypoint-py-ssrf-nonliteral-url
    return httpx.get(url)


def fetch_fixed():
    # WAYPOINT-OK: literal URL, no SSRF surface
    return requests.get("https://example.com/health", timeout=5).text


def hash_md5(data):
    # WAYPOINT-PLANT: waypoint-py-weak-hash
    return hashlib.md5(data).hexdigest()


def hash_sha1(data):
    # WAYPOINT-PLANT: waypoint-py-weak-hash
    return hashlib.sha1(data).hexdigest()


def hash_sha256(data):
    # WAYPOINT-OK: strong hash
    return hashlib.sha256(data).hexdigest()


def old_tls_context():
    # WAYPOINT-PLANT: waypoint-py-weak-tls-proto
    return ssl.SSLContext(ssl.PROTOCOL_TLSv1)


def ecb_cipher(key):
    # WAYPOINT-PLANT: waypoint-py-cipher-ecb
    return AES.new(key, AES.MODE_ECB)


def gen_token():
    # WAYPOINT-PLANT: waypoint-py-insecure-random
    return random.randint(0, 999999)


def gen_choice(alphabet):
    # WAYPOINT-PLANT: waypoint-py-insecure-random
    return random.choice(alphabet)


def gen_float():
    # WAYPOINT-PLANT: waypoint-py-insecure-random
    return random.random()


def run_app_debug():
    # WAYPOINT-PLANT: waypoint-py-flask-debug
    app.run(host="0.0.0.0", debug=True)


def run_app_safe():
    # WAYPOINT-OK: debug not enabled
    app.run(host="127.0.0.1")


# WAYPOINT-PLANT: waypoint-py-hardcoded-secret
API_KEY = "EXAMPLE-not-a-real-stripe-key"
# WAYPOINT-PLANT: waypoint-py-hardcoded-secret
db_password = "hunter2-super-secret-value"
# WAYPOINT-PLANT: waypoint-py-hardcoded-secret
ACCESS_TOKEN = "EXAMPLE-not-a-real-github-token"
# WAYPOINT-OK: value comes from the environment, not a literal
API_KEY_FROM_ENV = os.environ.get("API_KEY")


def parse_xml_lxml(xml_bytes):
    # WAYPOINT-PLANT: waypoint-py-xxe
    return lxml.etree.fromstring(xml_bytes)


def parse_xml_etree(path):
    # WAYPOINT-PLANT: waypoint-py-xxe
    return ET.parse(path)


def extract_zip(path, dest):
    # WAYPOINT-PLANT: waypoint-py-archive-extractall
    zipfile.ZipFile(path).extractall(dest)


def extract_tar(path, dest):
    # WAYPOINT-PLANT: waypoint-py-archive-extractall
    tarfile.open(path).extractall(dest)


def run_popen(cmd):
    # WAYPOINT-PLANT: waypoint-py-os-popen-system
    return os.popen(cmd).read()


def run_system(cmd):
    # WAYPOINT-PLANT: waypoint-py-os-popen-system
    os.system(cmd)


def raw_query(model, term):
    # WAYPOINT-PLANT: waypoint-py-django-raw-sql
    return model.objects.raw("SELECT * FROM t WHERE name = '%s'" % term)


def extra_query(qs, term):
    # WAYPOINT-PLANT: waypoint-py-django-raw-sql
    return qs.extra(where=["name = '%s'" % term])


# ---------------------------------------------------------------------------
# EDGE-CASE
# ---------------------------------------------------------------------------

# WAYPOINT-PLANT: waypoint-py-mutable-default-arg
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket


# WAYPOINT-PLANT: waypoint-py-mutable-default-arg
def with_opts(opts={}):
    return opts


# WAYPOINT-PLANT: waypoint-py-mutable-default-arg
def with_dict(d=dict()):
    return d


# WAYPOINT-OK: immutable default
def add_item_safe(item, bucket=None):
    bucket = bucket if bucket is not None else []
    bucket.append(item)
    return bucket


def fetch_no_timeout(url):
    # WAYPOINT-PLANT: waypoint-py-request-no-timeout
    return requests.get(url)


def post_no_timeout(url, payload):
    # WAYPOINT-PLANT: waypoint-py-request-no-timeout
    return requests.post(url, json=payload)


def fetch_with_timeout(url):
    # WAYPOINT-OK: timeout provided
    return requests.get(url, timeout=10)


def validate_amount(amount):
    # WAYPOINT-PLANT: waypoint-py-assert-validation
    assert amount > 0
    return amount


def open_no_with(path):
    # WAYPOINT-PLANT: waypoint-py-open-without-with
    f = open(path)
    data = f.read()
    return data


def open_with_ctx(path):
    # WAYPOINT-OK: context manager closes the handle
    with open(path) as f:
        return f.read()


# ---------------------------------------------------------------------------
# ABUSE
# ---------------------------------------------------------------------------

def read_all(resp):
    # WAYPOINT-PLANT: waypoint-py-unbounded-read
    return resp.read()


def read_capped(resp):
    # WAYPOINT-OK: bounded read
    return resp.read(8192)


def allocate(n):
    # WAYPOINT-PLANT: waypoint-py-input-driven-alloc
    return [0] * n


def make_range(n):
    # WAYPOINT-PLANT: waypoint-py-input-driven-alloc
    return list(range(n))


# ---------------------------------------------------------------------------
# CONCURRENCY
# ---------------------------------------------------------------------------

async def blocking_sleep_in_async():
    # WAYPOINT-PLANT: waypoint-py-blocking-call-in-async
    time.sleep(5)
    return "done"


async def blocking_request_in_async(url):
    # WAYPOINT-PLANT: waypoint-py-blocking-call-in-async
    return requests.get(url, timeout=5).text


async def non_blocking_async():
    # WAYPOINT-OK: awaits an async sleep, does not block the loop
    await asyncio.sleep(5)
    return "done"


async def fire_and_forget():
    # WAYPOINT-PLANT: waypoint-py-fire-and-forget-task
    asyncio.create_task(blocking_sleep_in_async())
    return "scheduled"


async def awaited_task():
    # WAYPOINT-OK: task handle is stored
    t = asyncio.create_task(blocking_sleep_in_async())
    await t
