// Intentionally hazardous sample code -- Waypoint hardening2 test fixture.
// Do not deploy. Each `// WAYPOINT-PLANT: <rule-id>` comment precedes a line that
// should fire that rule; `// WAYPOINT-OK:` lines are safe counterparts that
// should NOT fire. The file only needs to parse and be scannable.
import axios from "axios";
import http from "http";
import https from "https";
import vm from "vm";
import cors from "cors";
import cookie from "cookie";

declare const prisma: any;

// --------------------------------------------------------------------- security

export async function fetchDynamic(url: string) {
  // WAYPOINT-PLANT: waypoint-ts-ssrf-nonliteral-url
  return axios.get(url);
}

export async function fetchDynamicFetch(url: string) {
  // WAYPOINT-PLANT: waypoint-ts-ssrf-nonliteral-url
  return fetch(url);
}

export function fetchDynamicHttp(url: string) {
  // WAYPOINT-PLANT: waypoint-ts-ssrf-nonliteral-url
  return https.get(url);
}

export async function fetchFixed() {
  // WAYPOINT-OK: literal URL, no SSRF surface
  return axios.get("https://example.com/health");
}

export function setSessionCookie(res: any, token: string) {
  // WAYPOINT-PLANT: waypoint-ts-insecure-cookie
  res.cookie("session", token);
}

export function serializeCookie(token: string) {
  // WAYPOINT-PLANT: waypoint-ts-insecure-cookie
  return cookie.serialize("session", token);
}

export function setSessionCookieSafe(res: any, token: string) {
  // WAYPOINT-OK: hardened cookie flags
  res.cookie("session", token, { httpOnly: true, secure: true, sameSite: "strict" });
}

export function corsWildcard() {
  // WAYPOINT-PLANT: waypoint-ts-cors-wildcard
  return cors({ origin: "*" });
}

export function corsReflectAny() {
  // WAYPOINT-PLANT: waypoint-ts-cors-wildcard
  return cors({ origin: true });
}

export function corsSafe() {
  // WAYPOINT-OK: explicit trusted origin
  return cors({ origin: "https://app.example.com" });
}

export function runUserCode(src: string) {
  // WAYPOINT-PLANT: waypoint-ts-vm-runincontext
  return vm.runInNewContext(src, {});
}

export function runFixedCode() {
  // WAYPOINT-OK: literal code body
  return vm.runInNewContext("1 + 1", {});
}

// -------------------------------------------------------------------- edge-case

export function loadConfig(p: Promise<string>) {
  // WAYPOINT-PLANT: waypoint-ts-unhandled-promise
  p.then((cfg) => console.log(cfg));
}

export function loadConfigHandled(p: Promise<string>) {
  // WAYPOINT-OK: rejection handled
  p.then((cfg) => console.log(cfg)).catch((err) => console.error(err));
}

export function firstName(parts: string[], idx: number) {
  // WAYPOINT-PLANT: waypoint-ts-unguarded-computed-index
  return parts[idx].toUpperCase();
}

export function firstNameSafe(parts: string[]) {
  // WAYPOINT-OK: literal index, statically known
  return parts[0]?.toUpperCase();
}

// ------------------------------------------------------------------ concurrency

export function delay(ms: number) {
  // WAYPOINT-PLANT: waypoint-ts-promise-executor-no-reject
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

export function delaySafe(ms: number) {
  // WAYPOINT-OK: executor exposes reject for error paths
  return new Promise((resolve, reject) => {
    if (ms < 0) reject(new Error("negative"));
    setTimeout(resolve, ms);
  });
}

let requestCount = 0;

export async function handleRequest() {
  // WAYPOINT-PLANT: waypoint-ts-shared-counter-multi-async
  requestCount++;
  await Promise.resolve();
}

export async function alsoHandle(n: number) {
  // WAYPOINT-PLANT: waypoint-ts-shared-counter-multi-async
  requestCount += n;
  await Promise.resolve();
}

// ----------------------------------------------------------------------- abuse

export async function listAllUsers() {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-findmany
  return prisma.user.findMany();
}

export async function listActiveUsers() {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-findmany
  return prisma.user.findMany({ where: { active: true } });
}

export async function listUsersPaged(skip: number) {
  // WAYPOINT-OK: bounded by take
  return prisma.user.findMany({ skip, take: 50 });
}
