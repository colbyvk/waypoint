// Authz fixtures — WAYPOINT-PLANT fires, WAYPOINT-OK must not.
type U = { role: string; isAdmin: boolean; loggedIn: boolean };

export function Panel({ user }: { user: U }) {
  return (
    <div>
      {/* WAYPOINT-PLANT: waypoint-react-authz-clientside-guard */}
      {user.isAdmin && <button>Delete everything</button>}
      {/* WAYPOINT-OK: login state, not a privilege gate */}
      {user.loggedIn && <span>Welcome</span>}
    </div>
  );
}
