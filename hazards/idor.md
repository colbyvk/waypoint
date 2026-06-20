# Lookup by user-supplied id with no ownership check (IDOR)

- **Axes:** security, abuse
- **Languages:** Python
- **Generated rule(s):** `waypoint-py-idor-lookup-by-id`
- **Agent hypothesis:** "lookup by user-supplied id — missing ownership/authorization check (IDOR)?"

## What it is
The code fetches a record straight from an id the caller supplied — `Model.query.get(id)`,
`Model.objects.get(id=...)`, `session.get(Model, id)`, and friends — and hands the row
back. The hazard (an Insecure Direct Object Reference) is when nothing ties that id to
the *current user*: anyone can change the id in the URL and read someone else's record.
The flag marks the lookup shape. Whether an ownership/authorization check exists nearby
is a judgment only the agent can make, so this is a low-severity beacon by design.

## Bad (flagged)
```python
# samples/monorepo/py_service/app.py
@app.route("/item")
def get_item():
    item_id = request.args.get("id")
    row = db.fetch_item_by_id(item_id)   # fetched by raw id; no owner check
    return jsonify(row)
```

## Acceptable (not a problem)
```python
# samples/monorepo/py_service/app.py
@app.route("/myitem")
def get_my_item():
    item_id = request.args.get("id")
    user_id = request.headers.get("X-User-Id")
    # lookup is scoped to the current user; a foreign id returns nothing
    row = db.fetch_item_for_user(item_id, user_id)
    if row is None:
        return jsonify({"error": "not found or forbidden"}), 404
    return jsonify(row)
```

## Notes for the agent
- **Confirms a real concern:** the id comes from the request AND the row is returned
  (or modified) with no check that it belongs to the authenticated caller — no owner
  column in the query, no per-user filter, no authorization guard before the return.
- **Dismisses it:** the lookup is scoped to the current user (an `owner`/`user_id`
  filter, a per-tenant session), an explicit authorization check precedes the
  return, or the record is genuinely public.
- Look a few lines up and down from the lookup — the ownership check, if present, is
  usually right next to it (as in the acceptable example above).
