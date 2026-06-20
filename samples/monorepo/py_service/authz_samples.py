"""Authz / access-control fixtures — WAYPOINT-PLANT fires, WAYPOINT-OK must not."""
from flask import Flask, request

app = Flask(__name__)


class User:
    pass


@app.route("/admin/delete")
def admin_delete():
    # WAYPOINT-PLANT: waypoint-py-authz-route-no-auth (no auth decorator)
    return "deleted"


@app.route("/me")
@login_required  # noqa: F821
def me():
    # WAYPOINT-OK: auth decorator present (below the route)
    return "me"


@login_required  # noqa: F821
@app.route("/me2")
def me2():
    # WAYPOINT-OK: auth decorator present (above the route)
    return "me2"


def create_user():
    # WAYPOINT-PLANT: waypoint-py-authz-mass-assignment
    return User(**request.get_json())


def create_user_ok():
    # WAYPOINT-OK: explicit, whitelisted field
    u = User()
    u.name = request.json["name"]
    return u


def set_priv(user):
    # WAYPOINT-PLANT: waypoint-py-authz-privilege-from-request
    user.is_admin = request.json["is_admin"]
    return user


def set_priv_ok(user):
    # WAYPOINT-OK: privilege not taken from request
    user.is_admin = False
    return user
