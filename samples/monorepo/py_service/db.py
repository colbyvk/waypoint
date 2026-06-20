# Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import sqlite3

conn = sqlite3.connect("app.db", check_same_thread=False)


def find_user(name):
    cur = conn.cursor()
    # WAYPOINT-PLANT: PY-SQL-STRING [axes: security,abuse]
    cur.execute("SELECT * FROM users WHERE name = '%s'" % name)
    return cur.fetchall()


def fetch_item_by_id(item_id):
    cur = conn.cursor()
    # WAYPOINT-PLANT: PY-SQL-STRING [axes: security,abuse]
    cur.execute(f"SELECT * FROM items WHERE id = {item_id}")
    return cur.fetchone()


def fetch_item_for_user(item_id, user_id):
    cur = conn.cursor()
    # WAYPOINT-OK: parametrized query with bound params
    cur.execute("SELECT * FROM items WHERE id = ? AND owner = ?", (item_id, user_id))
    return cur.fetchone()


def safe_find_user(name):
    cur = conn.cursor()
    # WAYPOINT-OK: parametrized query, no string interpolation
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    return cur.fetchall()
