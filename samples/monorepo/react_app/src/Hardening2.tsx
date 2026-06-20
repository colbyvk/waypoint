// Intentionally hazardous sample code -- Waypoint hardening2 test fixture.
// Do not deploy. Each `// WAYPOINT-PLANT: <rule-id>` comment precedes a line that
// should fire that rule; `// WAYPOINT-OK:` lines are safe counterparts that
// should NOT fire. The file only needs to parse and be scannable.
import React from "react";

// ---------------------------------------------------------------------- security

export function LoginForm() {
  function onSubmit(token: string) {
    // WAYPOINT-PLANT: waypoint-react-token-in-webstorage
    localStorage.setItem("auth_token", token);
  }
  function onSubmitSession(token: string) {
    // WAYPOINT-PLANT: waypoint-react-token-in-webstorage
    sessionStorage.setItem("jwt", token);
  }
  function rememberTheme(value: string) {
    // WAYPOINT-OK: non-sensitive key persisted in web storage
    localStorage.setItem("theme", value);
  }
  return <button onClick={() => onSubmit("x")}>Login</button>;
}

export function ApiPanel() {
  // WAYPOINT-PLANT: waypoint-react-process-env-in-client
  const key = process.env.STRIPE_SECRET_KEY;
  // WAYPOINT-OK: public, non-secret config is fine to inline
  const base = process.env.PUBLIC_API_URL;
  return <div data-base={base}>{key ? "configured" : "missing"}</div>;
}

export function Feed() {
  function load() {
    // WAYPOINT-PLANT: waypoint-react-insecure-http-url
    return fetch("http://api.example.com/feed");
  }
  function loadSecure() {
    // WAYPOINT-OK: https transport
    return fetch("https://api.example.com/feed");
  }
  return (
    <div>
      {/* WAYPOINT-PLANT: waypoint-react-insecure-http-url */}
      <a href="http://example.com/legacy">Legacy</a>
      {/* WAYPOINT-OK: https link */}
      <a href="https://example.com/home">Home</a>
    </div>
  );
}
