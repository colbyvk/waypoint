"""
suppress.py — the suppression store + allowlist (spec §9).

Two ways a beacon gets suppressed:
  1. content-hash store  — an agent dismissed this exact region before; the
     verdict is remembered until it expires OR the region's code changes (the
     hash is over normalized region text, so an edit re-raises it naturally).
  2. allowlist.yaml      — a human pre-accepted a pattern, WITH a written
     justification and an expiry date.

Both carry expiry so nothing is suppressed forever. Pure stdlib + PyYAML.
Imported by prioritise/rank.py (same dir) and the dispatcher (writes verdicts
back here).
"""
from __future__ import annotations
import datetime as _dt
import json
import os
from typing import Any

import yaml

# verdicts that mean "do not re-raise"
DISMISSED = {"dismiss", "dismissed", "false-positive", "false_positive", "accepted", "wontfix"}


def today() -> _dt.date:
    return _dt.date.today()


def _parse_date(s: str | None) -> _dt.date | None:
    if not s:
        return None
    try:
        return _dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


# --------------------------------------------------------------------------- #
# store.json : { "version": 1, "suppressions": [ {entry}, ... ] }
# entry = {content_hash, verdict, rule_id, file, expiry, by, note, recorded_at}
# --------------------------------------------------------------------------- #
def load_store(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {"version": 1, "suppressions": []}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("suppressions", [])
    return data


def save_store(path: str, store: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)
        fh.write("\n")


def match_store(content_hash: str, store: dict, ref: _dt.date | None = None) -> dict | None:
    """Return the active suppression entry for this hash, or None.

    Active = verdict is a dismissal AND (no expiry OR expiry >= today).
    Expired entries are ignored so the region is re-examined (spec §9 expiry).
    """
    ref = ref or today()
    for e in store.get("suppressions", []):
        if e.get("content_hash") != content_hash:
            continue
        if str(e.get("verdict", "")).lower() not in DISMISSED:
            continue
        exp = _parse_date(e.get("expiry"))
        if exp is not None and exp < ref:
            continue  # expired -> re-raise
        return e
    return None


def record_dismissals(path: str, entries: list[dict], default_expiry_days: int = 90,
                      ref: _dt.date | None = None) -> dict:
    """Upsert dismissal entries into the store by content_hash. Returns the store."""
    ref = ref or today()
    store = load_store(path)
    by_hash = {e.get("content_hash"): e for e in store["suppressions"]}
    for ent in entries:
        h = ent.get("content_hash")
        if not h:
            continue
        ent.setdefault("recorded_at", ref.isoformat())
        ent.setdefault("expiry", (ref + _dt.timedelta(days=default_expiry_days)).isoformat())
        by_hash[h] = {**by_hash.get(h, {}), **ent}
    store["suppressions"] = list(by_hash.values())
    save_store(path, store)
    return store


# --------------------------------------------------------------------------- #
# allowlist.yaml : list of { rule_id?, path?, content_hash?, justification, expiry }
# A beacon matches an entry when every present selector matches; justification +
# expiry are REQUIRED (entries missing them are reported and ignored).
# --------------------------------------------------------------------------- #
def load_allowlist(path: str) -> list[dict]:
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if isinstance(data, dict):
        items = data.get("allow")
        if items is None:                 # a single entry written at the root
            items = [data] if data else []
    else:
        items = data or []
    if not isinstance(items, list):
        items = [items]
    return [e for e in items if isinstance(e, dict)]   # drop malformed entries


def allowlist_problems(allowlist: list[dict]) -> list[str]:
    """Entries lacking a justification or expiry — surfaced, never silently used."""
    probs = []
    for i, e in enumerate(allowlist):
        if not e.get("justification"):
            probs.append(f"allowlist[{i}] missing 'justification'")
        if not _parse_date(e.get("expiry")):
            probs.append(f"allowlist[{i}] missing/invalid 'expiry' (YYYY-MM-DD)")
    return probs


def match_allowlist(rule_ids: list[str], file_uri: str, content_hash: str,
                    allowlist: list[dict], ref: _dt.date | None = None) -> dict | None:
    import fnmatch
    ref = ref or today()
    file_uri = (file_uri or "").replace("\\", "/")
    for e in allowlist:
        if not e.get("justification") or not _parse_date(e.get("expiry")):
            continue  # invalid entries never suppress
        if _parse_date(e["expiry"]) < ref:
            continue  # expired
        selectors_present = False
        if e.get("content_hash"):
            selectors_present = True
            if e["content_hash"] != content_hash:
                continue
        if e.get("rule_id"):
            selectors_present = True
            if not any(fnmatch.fnmatch(r, e["rule_id"]) for r in rule_ids):
                continue
        if e.get("path"):
            selectors_present = True
            pat = e["path"]
            if not (fnmatch.fnmatch(file_uri, pat) or fnmatch.fnmatch("/" + file_uri, pat)):
                continue
        if selectors_present:
            return e
    return None
