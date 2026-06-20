# SQL built by string interpolation reaching execute() (Python)

- **Axes:** security, abuse
- **Languages:** Python
- **Generated rule(s):** `waypoint-py-sql-string-build`
- **Agent hypothesis:** "string-built SQL into execute() — injection if input is untrusted?"

## What it is
A SQL query string is assembled with an f-string, `%`-formatting, or `+`
concatenation, and that string is handed straight to `execute()` / `executemany()`.
When a value is glued into the query text this way, the database cannot tell the
difference between the query and the data — so a crafted input can change what the
query *does* (SQL injection). The flag marks every query built by string-stitching;
whether the stitched-in value is actually untrusted is the agent's call.

## Bad (flagged)
```python
# samples/monorepo/py_service/db.py
def find_user(name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = '%s'" % name)   # % into query text
    return cur.fetchall()

def fetch_item_by_id(item_id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM items WHERE id = {item_id}")      # f-string into query
    return cur.fetchone()
```

## Acceptable (not a problem)
```python
# samples/monorepo/py_service/db.py
def safe_find_user(name):
    cur = conn.cursor()
    # value passed as a bound parameter, not stitched into the query text
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cur.fetchall()
```

## Notes for the agent
- **Confirms a real concern:** a value that can come from a request, a header, a
  filename, or any other external source reaches the stitched query without being
  passed as a bound parameter.
- **Dismisses it:** the interpolated value is a hard-coded constant or comes from a
  trusted, fixed allow-list (e.g. a validated column name from an enum), or the
  query already uses `?` / `%s` placeholders with a params tuple.
- The fix is almost always "move the value into the parameters tuple" — note that
  if recommending a change.
