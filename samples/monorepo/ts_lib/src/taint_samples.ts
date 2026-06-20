// Taint-flow fixtures — WAYPOINT-PLANT should fire (input reaches sink),
// WAYPOINT-OK must not (constant / parametrized).
import * as cp from "child_process";
import axios from "axios";

declare const req: any;
declare const res: any;
declare const db: any;
declare const el: any;

export function xss() {
  // WAYPOINT-PLANT: waypoint-ts-taint-xss
  el.innerHTML = req.query.html;
  // WAYPOINT-OK: constant html
  el.innerHTML = "<b>safe</b>";
}

export function command() {
  // WAYPOINT-PLANT: waypoint-ts-taint-command
  cp.exec("ls " + req.query.dir);
  // WAYPOINT-OK: constant command
  cp.exec("ls -la");
}

export function sql() {
  // WAYPOINT-PLANT: waypoint-ts-taint-sql
  db.query("SELECT * FROM u WHERE n = '" + req.body.name + "'");
  // WAYPOINT-OK: parametrized — query string is constant
  db.query("SELECT * FROM u WHERE n = $1", [req.body.name]);
}

export function ssrf() {
  // WAYPOINT-PLANT: waypoint-ts-taint-ssrf
  axios.get(req.query.url);
  // WAYPOINT-OK: constant url
  axios.get("https://api.internal/health");
}

export function redirect() {
  // WAYPOINT-PLANT: waypoint-ts-taint-redirect
  res.redirect(req.query.next);
  // WAYPOINT-OK: constant target
  res.redirect("/home");
}
