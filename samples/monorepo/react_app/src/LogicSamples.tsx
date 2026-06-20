import { useState, useEffect } from "react";

// Logic-smell fixtures — WAYPOINT-PLANT should fire, WAYPOINT-OK must not.

export function ConditionalHook({ enabled }: { enabled: boolean }) {
  // WAYPOINT-PLANT: waypoint-react-logic-conditional-hook
  if (enabled) {
    const [n, setN] = useState(0);
    return <div onClick={() => setN(n + 1)}>{n}</div>;
  }
  return null;
}

export function MissingDeps({ id }: { id: string }) {
  // WAYPOINT-PLANT: waypoint-react-logic-effect-no-deps
  useEffect(() => {
    console.log(id);
  });
  // WAYPOINT-OK: explicit dependency array
  useEffect(() => {
    console.log(id);
  }, [id]);
  return null;
}

export function OkHook() {
  // WAYPOINT-OK: hook at top level, called unconditionally
  const [n, setN] = useState(0);
  return <div onClick={() => setN(n + 1)}>{n}</div>;
}
