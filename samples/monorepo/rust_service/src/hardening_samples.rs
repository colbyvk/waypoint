// Intentionally hazardous sample code -- Waypoint hardening test fixture.
// Do not deploy. Each `WAYPOINT-PLANT` line should trigger the named rule;
// `WAYPOINT-OK` lines are safe counterparts that should NOT trigger.
//
// This file is meant to PARSE, not necessarily fully type-check. Some calls
// reference crates (sqlx) not in Cargo.toml; that is fine for Semgrep.
#![allow(unused, dead_code)]

use std::collections::HashMap;
use std::io::Read;
use std::mem;
use std::process::Command;
use std::rc::Rc;
use std::sync::Mutex;
use std::thread;

// ------------------------------------------------------------------ security

pub unsafe fn deref_raw(p: *const u8) -> u8 {
    // WAYPOINT-PLANT: waypoint-rust-unsafe-block
    let v = unsafe { *p };
    v
}

pub fn reinterpret(x: u64) -> f64 {
    // WAYPOINT-PLANT: waypoint-rust-mem-transmute
    unsafe { mem::transmute(x) }
}

pub fn reinterpret_full(x: i64) -> u64 {
    // WAYPOINT-PLANT: waypoint-rust-mem-transmute
    unsafe { std::mem::transmute(x) }
}

pub fn first_byte(buf: &[u8], i: usize) -> u8 {
    // WAYPOINT-PLANT: waypoint-rust-unchecked-access
    unsafe { *buf.get_unchecked(i) }
}

pub fn first_byte_mut(buf: &mut [u8], i: usize) -> &mut u8 {
    // WAYPOINT-PLANT: waypoint-rust-unchecked-access
    unsafe { buf.get_unchecked_mut(i) }
}

pub fn as_text(bytes: &[u8]) -> &str {
    // WAYPOINT-PLANT: waypoint-rust-unchecked-access
    unsafe { std::str::from_utf8_unchecked(bytes) }
}

// WAYPOINT-OK: checked access via .get() returns Option
pub fn first_byte_safe(buf: &[u8], i: usize) -> Option<&u8> {
    buf.get(i)
}

pub async fn lookup_user(pool: &sqlx::PgPool, name: &str) {
    // WAYPOINT-PLANT: waypoint-rust-sql-format
    let q = sqlx::query(&format!("SELECT * FROM users WHERE name = '{}'", name));
    // WAYPOINT-PLANT: waypoint-rust-sql-format
    let q2 = sqlx::query(format!("DELETE FROM users WHERE name = '{}'", name));
    let _ = (q, q2);
}

pub fn run_via_conn(conn: &Connection, table: &str) {
    // WAYPOINT-PLANT: waypoint-rust-sql-format
    conn.execute(&format!("DROP TABLE {}", table));
    // WAYPOINT-PLANT: waypoint-rust-sql-format
    conn.query(format!("SELECT * FROM {}", table));
}

// WAYPOINT-OK: parameterized query, no string interpolation of input
pub async fn lookup_user_safe(pool: &sqlx::PgPool, name: &str) {
    let _ = sqlx::query("SELECT * FROM users WHERE name = $1");
}

pub fn run_dynamic_program(program: &str) -> std::io::Result<std::process::Output> {
    // WAYPOINT-PLANT: waypoint-rust-command-dynamic-program
    Command::new(program).arg("--version").output()
}

pub fn run_dynamic_program_full(program: String) -> std::io::Result<std::process::Output> {
    // WAYPOINT-PLANT: waypoint-rust-command-dynamic-program
    std::process::Command::new(program).output()
}

// WAYPOINT-OK: fixed literal program name
pub fn run_fixed_program() -> std::io::Result<std::process::Output> {
    Command::new("ls").arg("-la").output()
}

// WAYPOINT-PLANT: waypoint-rust-hardcoded-secret
const API_KEY: &str = "sk-live-1234567890abcdef";

// WAYPOINT-PLANT: waypoint-rust-hardcoded-secret
static DB_PASSWORD: &str = "hunter2-prod-pw";

pub fn connect() {
    // WAYPOINT-PLANT: waypoint-rust-hardcoded-secret
    let auth_token = "Bearer abc.def.ghi";
    // WAYPOINT-PLANT: waypoint-rust-hardcoded-secret
    let secret: &str = "topsecretvalue";
    let _ = (auth_token, secret);
}

// WAYPOINT-OK: secret read from environment, not a literal
pub fn connect_safe() {
    let api_key = std::env::var("API_KEY").unwrap_or_default();
    let _ = api_key;
}

// ----------------------------------------------------------------- edge-case

pub fn load_config(raw: Option<String>) -> String {
    // WAYPOINT-PLANT: waypoint-rust-panic-family
    raw.expect("config must be present")
}

pub fn dispatch(kind: u8) -> u8 {
    match kind {
        0 => 10,
        1 => 20,
        // WAYPOINT-PLANT: waypoint-rust-panic-family
        _ => unreachable!("unexpected kind"),
    }
}

pub fn not_done() {
    // WAYPOINT-PLANT: waypoint-rust-panic-family
    todo!("implement later")
}

pub fn missing() {
    // WAYPOINT-PLANT: waypoint-rust-panic-family
    unimplemented!("not built yet")
}

pub fn boom(cond: bool) {
    if cond {
        // WAYPOINT-PLANT: waypoint-rust-panic-family
        panic!("explicit abort");
    }
}

// WAYPOINT-OK: handled with a default instead of panicking
pub fn load_config_safe(raw: Option<String>) -> String {
    raw.unwrap_or_else(|| "default".to_string())
}

pub fn shrink(big: u64) -> u8 {
    // WAYPOINT-PLANT: waypoint-rust-lossy-cast
    let small = big as u8;
    // WAYPOINT-PLANT: waypoint-rust-lossy-cast
    let mid = big as u32;
    let _ = mid;
    small
}

pub fn shrink_signed(n: i64) -> i32 {
    // WAYPOINT-PLANT: waypoint-rust-lossy-cast
    n as i32
}

// WAYPOINT-OK: widening cast cannot lose information
pub fn widen(small: u8) -> u64 {
    small as u64
}

pub fn nth(items: &[i32], idx: usize) -> i32 {
    // WAYPOINT-PLANT: waypoint-rust-panicking-index
    items[idx]
}

pub fn first(items: &Vec<i32>) -> i32 {
    let i = compute_index();
    // WAYPOINT-PLANT: waypoint-rust-panicking-index
    items[i]
}

// WAYPOINT-OK: bounds-checked access via .get()
pub fn nth_safe(items: &[i32], idx: usize) -> Option<&i32> {
    items.get(idx)
}

fn compute_index() -> usize {
    0
}

// --------------------------------------------------------------------- abuse

pub fn preallocate(n: usize) -> Vec<u8> {
    // WAYPOINT-PLANT: waypoint-rust-alloc-from-size
    let mut v: Vec<u8> = Vec::with_capacity(n);
    // WAYPOINT-PLANT: waypoint-rust-alloc-from-size
    v.reserve(n);
    v
}

pub fn fill(count: usize) -> Vec<u32> {
    // NOTE: `vec![x; n]` is not matchable as a Semgrep Rust pattern (macro
    // repeat form), so it is intentionally NOT planted here. The reserve/
    // with_capacity arms below cover the same memory-amplification hazard.
    vec![0u32; count]
}

pub fn build_string(cap: usize) -> String {
    // WAYPOINT-PLANT: waypoint-rust-alloc-from-size
    String::with_capacity(cap)
}

// WAYPOINT-OK: fixed, literal capacity
pub fn preallocate_fixed() -> Vec<u8> {
    Vec::with_capacity(1024)
}

pub fn slurp<R: Read>(mut r: R) -> std::io::Result<Vec<u8>> {
    let mut buf = Vec::new();
    // WAYPOINT-PLANT: waypoint-rust-read-unbounded
    r.read_to_end(&mut buf)?;
    Ok(buf)
}

pub fn slurp_string<R: Read>(mut r: R) -> std::io::Result<String> {
    let mut s = String::new();
    // WAYPOINT-PLANT: waypoint-rust-read-unbounded
    r.read_to_string(&mut s)?;
    Ok(s)
}

pub fn slurp_file(path: &str) -> std::io::Result<String> {
    // WAYPOINT-PLANT: waypoint-rust-read-unbounded
    std::fs::read_to_string(path)
}

// WAYPOINT-OK: bounded read via take(limit)
pub fn slurp_bounded<R: Read>(r: R) -> std::io::Result<Vec<u8>> {
    let mut buf = Vec::new();
    r.take(4096).read_to_end(&mut buf)?;
    Ok(buf)
}

// --------------------------------------------------------------- concurrency

pub async fn guarded_update(m: &Mutex<u64>) {
    // WAYPOINT-PLANT: waypoint-rust-lock-across-await
    let mut g = m.lock().unwrap();
    *g += 1;
    do_async_work().await;
}

pub async fn guarded_update_async(m: &tokio::sync::Mutex<u64>) {
    // WAYPOINT-PLANT: waypoint-rust-lock-across-await
    let mut g = m.lock().await;
    *g += 1;
    do_async_work().await;
}

async fn do_async_work() {}

// WAYPOINT-OK: synchronous function, no await -> guard cannot cross an await.
// (Note: the proxy rule is recall-biased; a scoped guard dropped before an
// await inside an async fn would still match and is left for the agent to
// verify. This sync example is a clean true-negative.)
pub fn guarded_update_safe(m: &Mutex<u64>) {
    let mut g = m.lock().unwrap();
    *g += 1;
}

pub fn spawn_with_rc() {
    // WAYPOINT-PLANT: waypoint-rust-rc-near-spawn
    let shared = Rc::new(42u64);
    let h = thread::spawn(move || {
        println!("worker");
    });
    let _ = (shared, h.join());
}

// WAYPOINT-OK: no spawn nearby, plain single-threaded Rc use
pub fn local_rc() -> u64 {
    let shared = Rc::new(7u64);
    *shared
}

// ----------------------------------------------------- stubs to aid parsing
pub struct Connection;
impl Connection {
    pub fn execute(&self, _q: &str) {}
    pub fn query(&self, _q: String) {}
}

mod sqlx {
    pub struct PgPool;
    pub struct Query;
    pub fn query<T>(_q: T) -> Query {
        Query
    }
}
