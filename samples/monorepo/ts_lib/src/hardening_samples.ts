// Intentionally hazardous sample code -- Waypoint hardening test fixture. Do not deploy.
// Each WAYPOINT-PLANT comment names the rule expected to fire on the following line.
// WAYPOINT-OK lines are safe counterparts that must NOT fire.

import * as fs from "fs";
import { spawn, execFile } from "child_process";
import jwt from "jsonwebtoken";

declare const knex: any;
declare const sequelize: any;
declare function doWork(): void;
declare function poll(): void;

// ---------------------------------------------------------------------------
// security: DOM XSS sinks
// ---------------------------------------------------------------------------
export function renderUnsafe(el: HTMLElement, data: string): void {
  // WAYPOINT-PLANT: waypoint-ts-dom-xss-sink
  el.innerHTML = data;
}
export function renderOuter(el: HTMLElement, data: string): void {
  // WAYPOINT-PLANT: waypoint-ts-dom-xss-sink
  el.outerHTML = data;
}
export function renderWrite(data: string): void {
  // WAYPOINT-PLANT: waypoint-ts-dom-xss-sink
  document.write(data);
}
export function renderAdjacent(el: HTMLElement, data: string): void {
  // WAYPOINT-PLANT: waypoint-ts-dom-xss-sink
  el.insertAdjacentHTML("beforeend", data);
}
// WAYPOINT-OK: static literal markup, no injection surface
export function renderStatic(el: HTMLElement): void {
  el.innerHTML = "<b>static</b>";
}

// ---------------------------------------------------------------------------
// security: SQL injection via template literal
// ---------------------------------------------------------------------------
export function findUser(db: any, name: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-sql-template-injection
  return db.query(`SELECT * FROM users WHERE name = '${name}'`);
}
export function rawQuery(id: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-sql-template-injection
  return knex.raw(`DELETE FROM sessions WHERE id = ${id}`);
}
export function seqQuery(role: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-sql-template-injection
  return sequelize.query(`SELECT * FROM users WHERE role = '${role}'`);
}
// WAYPOINT-OK: parameterized query, no interpolation
export function findUserSafe(db: any, name: string): unknown {
  return db.query("SELECT * FROM users WHERE name = ?", [name]);
}

// ---------------------------------------------------------------------------
// security: open redirect / location
// ---------------------------------------------------------------------------
export function gotoHref(target: string): void {
  // WAYPOINT-PLANT: waypoint-ts-open-redirect
  window.location.href = target;
}
export function gotoAssign(target: string): void {
  // WAYPOINT-PLANT: waypoint-ts-open-redirect
  location.assign(target);
}
export function serverRedirect(res: any, next: string): void {
  // WAYPOINT-PLANT: waypoint-ts-open-redirect
  res.redirect(next);
}
// WAYPOINT-OK: fixed internal destination
export function gotoHome(res: any): void {
  res.redirect("/home");
}

// ---------------------------------------------------------------------------
// security: child_process with shell
// ---------------------------------------------------------------------------
export function spawnShell(cmd: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-child-process-shell
  return spawn(cmd, [], { shell: true });
}
export function execFileShell(cmd: string, args: string[]): unknown {
  // WAYPOINT-PLANT: waypoint-ts-child-process-shell
  return execFile(cmd, args, { shell: true }, () => {});
}
// WAYPOINT-OK: no shell, args passed as an array
export function spawnSafe(args: string[]): unknown {
  return spawn("git", args, { shell: false });
}

// ---------------------------------------------------------------------------
// security: fs path traversal
// ---------------------------------------------------------------------------
export function readUserFile(p: string): Buffer {
  // WAYPOINT-PLANT: waypoint-ts-fs-path-traversal
  return fs.readFileSync(p);
}
export function streamUserFile(p: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-fs-path-traversal
  return fs.createReadStream(p);
}
export function writeUserFile(p: string, body: string): void {
  // WAYPOINT-PLANT: waypoint-ts-fs-path-traversal
  fs.writeFileSync(p, body);
}
// WAYPOINT-OK: fixed, known-safe path literal
export function readConfig(): Buffer {
  return fs.readFileSync("/etc/app/config.json");
}

// ---------------------------------------------------------------------------
// security: weak JWT
// ---------------------------------------------------------------------------
export function verifyNone(token: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-weak-jwt
  return jwt.verify(token, "secret", { algorithms: ["none"] });
}
export function decodeAsTrust(token: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-weak-jwt
  return jwt.decode(token);
}
export function signNone(payload: object): string {
  // WAYPOINT-PLANT: waypoint-ts-weak-jwt
  return jwt.sign(payload, "secret", { algorithm: "none" });
}
// WAYPOINT-OK: verifies with an explicit asymmetric algorithm
export function verifyStrong(token: string, pubKey: string): unknown {
  return jwt.verify(token, pubKey, { algorithms: ["RS256"] });
}

// ---------------------------------------------------------------------------
// security: hardcoded secret
// ---------------------------------------------------------------------------
// WAYPOINT-PLANT: waypoint-ts-hardcoded-secret
const password = "hunter2";
// WAYPOINT-PLANT: waypoint-ts-hardcoded-secret
let apiKey = "sk-live-9f8e7d6c5b4a";
// WAYPOINT-PLANT: waypoint-ts-hardcoded-secret
const access_token = "ya29.A0ARrdaM-token-value";
// WAYPOINT-OK: not a credential name
const username = "service-account";
// WAYPOINT-OK: value comes from the environment, not a literal
const sessionSecret = process.env.SESSION_SECRET || "";
export { apiKey, access_token, username, sessionSecret, password };

// ---------------------------------------------------------------------------
// security: postMessage / message origin
// ---------------------------------------------------------------------------
export function broadcast(child: Window, data: unknown): void {
  // WAYPOINT-PLANT: waypoint-ts-postmessage-origin
  child.postMessage(data, "*");
}
export function listen(): void {
  // WAYPOINT-PLANT: waypoint-ts-postmessage-origin
  window.addEventListener("message", (e: MessageEvent) => console.log(e.data));
}
// WAYPOINT-OK: explicit, specific target origin
export function broadcastSafe(child: Window, data: unknown): void {
  child.postMessage(data, "https://trusted.example.com");
}

// ---------------------------------------------------------------------------
// security: prototype pollution via merge
// ---------------------------------------------------------------------------
export function mergeConfig(target: Record<string, unknown>, raw: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-proto-pollution-merge
  return Object.assign(target, JSON.parse(raw));
}
// WAYPOINT-OK: re proto-pollution -- parsed once, not merged into an existing object.
// (Still fires waypoint-ts-json-parse-no-try by design; see parseSafe below for the guarded form.)
export function parseConfig(raw: string): unknown {
  return JSON.parse(raw);
}

// ---------------------------------------------------------------------------
// edge-case: loose equality
// ---------------------------------------------------------------------------
export function looseEq(a: unknown, b: unknown): boolean {
  // WAYPOINT-PLANT: waypoint-ts-loose-equality
  return a == b;
}
export function looseNeq(a: unknown, b: unknown): boolean {
  // WAYPOINT-PLANT: waypoint-ts-loose-equality
  return a != b;
}
// WAYPOINT-OK: strict equality, and == null is conventionally allowed
export function strictEq(a: unknown, b: unknown): boolean {
  return a === b;
}
export function isNullish(a: unknown): boolean {
  return a == null;
}

// ---------------------------------------------------------------------------
// edge-case: JSON.parse without try/catch
// ---------------------------------------------------------------------------
export function parseLoose(raw: string): unknown {
  // WAYPOINT-PLANT: waypoint-ts-json-parse-no-try
  const obj = JSON.parse(raw);
  return obj;
}
// WAYPOINT-OK: parse wrapped in try/catch with a fallback
export function parseSafe<T>(raw: string, fallback: T): T {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

// ---------------------------------------------------------------------------
// abuse: unbounded loop
// ---------------------------------------------------------------------------
export function spinForever(queue: string[]): void {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-loop
  while (true) {
    const item = queue.shift();
    if (item) doWork();
  }
}
export function spinClassic(): void {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-loop
  for (;;) {
    doWork();
  }
}
// WAYPOINT-OK: bounded loop over a finite collection
export function processAll(items: string[]): void {
  for (const _ of items) doWork();
}

// ---------------------------------------------------------------------------
// abuse: unbounded allocation
// ---------------------------------------------------------------------------
export function preallocate(n: number): unknown[] {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-allocation
  return new Array(n);
}
export function allocBuffer(size: number): Buffer {
  // WAYPOINT-PLANT: waypoint-ts-unbounded-allocation
  return Buffer.alloc(size);
}
// WAYPOINT-OK: fixed, small literal size
export function fixedBucket(): unknown[] {
  return new Array(16);
}

// ---------------------------------------------------------------------------
// concurrency: timer leak
// ---------------------------------------------------------------------------
export function startPolling(): void {
  // WAYPOINT-PLANT: waypoint-ts-timer-leak
  setInterval(() => poll(), 1000);
}
export function rescheduleSelf(): void {
  // WAYPOINT-PLANT: waypoint-ts-timer-leak
  setTimeout(() => {
    doWork();
    setTimeout(() => rescheduleSelf(), 500);
  }, 1000);
}
// WAYPOINT-PLANT: waypoint-ts-timer-leak
// Recall marker: setInterval always fires; here the handle is captured and cleared,
// so the verifier agent should rule this benign.
export function startStoppable(): () => void {
  const id = setInterval(() => poll(), 1000);
  return () => clearInterval(id);
}

// ---------------------------------------------------------------------------
// concurrency: shared mutable + async
// ---------------------------------------------------------------------------
let requestCounter = 0;
const auditTrail: number[] = [];

export async function trackRequest(): Promise<void> {
  // WAYPOINT-PLANT: waypoint-ts-shared-mutable-async
  requestCounter = requestCounter + 1;
  // WAYPOINT-PLANT: waypoint-ts-shared-mutable-async
  auditTrail.push(requestCounter);
}
// WAYPOINT-OK: pure function, mutates only a local
export function countLocal(items: string[]): number {
  let local = 0;
  for (const _ of items) local += 1;
  return local;
}
