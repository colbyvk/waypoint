# Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
from flask import Flask, request, jsonify
import db

app = Flask(__name__)


@app.route("/calc")
def calc():
    formula = request.args.get("formula", "1+1")
    # WAYPOINT-PLANT: PY-EXEC-EVAL [axes: security]
    result = eval(formula)
    return jsonify({"result": result})


@app.route("/item")
def get_item():
    item_id = request.args.get("id")
    # WAYPOINT-PLANT: PY-IDOR [axes: security,abuse]
    row = db.fetch_item_by_id(item_id)
    return jsonify(row)


@app.route("/myitem")
def get_my_item():
    item_id = request.args.get("id")
    user_id = request.headers.get("X-User-Id")
    # WAYPOINT-OK: ownership checked before returning the row
    row = db.fetch_item_for_user(item_id, user_id)
    if row is None:
        return jsonify({"error": "not found or forbidden"}), 404
    return jsonify(row)


if __name__ == "__main__":
    app.run()
