// Intentionally hazardous sample code -- Waypoint hardening2 test fixture.
// Do not deploy. Each `WAYPOINT-PLANT` line should trigger the named rule;
// `WAYPOINT-OK` lines are safe counterparts that should NOT trigger.
//
// This file is meant to PARSE, not necessarily fully type-check. Some calls
// reference crates (reqwest, openssl) not in Cargo.toml; that is fine for Semgrep.
#![allow(unused, dead_code)]

use std::cell::RefCell;
use std::env;
use std::path::PathBuf;
use std::rc::Rc;
use std::sync::mpsc;
use std::sync::{Arc, Mutex};
use std::thread;

// ------------------------------------------------------------------ security

pub async fn fetch_dynamic(url: String) -> String {
    // WAYPOINT-PLANT: waypoint-rust-ssrf-nonliteral-url
    reqwest::get(url).await.unwrap().text().await.unwrap()
}

pub async fn fetch_dynamic_client(client: &reqwest::Client, url: &str) {
    // WAYPOINT-PLANT: waypoint-rust-ssrf-nonliteral-url
    let _ = client.get(url).send().await;
}

pub async fn fetch_fixed() -> String {
    // WAYPOINT-OK: literal URL, no SSRF surface
    reqwest::get("https://example.com/health").await.unwrap().text().await.unwrap()
}

pub fn insecure_client() -> reqwest::Client {
    // WAYPOINT-PLANT: waypoint-rust-tls-verify-disabled
    reqwest::Client::builder().danger_accept_invalid_certs(true).build().unwrap()
}

pub fn insecure_ssl_mode(ctx: &mut openssl::ssl::SslContextBuilder) {
    // WAYPOINT-PLANT: waypoint-rust-tls-verify-disabled
    ctx.set_verify(SslVerifyMode::NONE);
}

pub fn predictable_temp() -> PathBuf {
    // WAYPOINT-PLANT: waypoint-rust-tempfile-predictable
    env::temp_dir().join("waypoint-cache.tmp")
}

pub fn fixed_tmp_path() -> PathBuf {
    // WAYPOINT-PLANT: waypoint-rust-tempfile-predictable
    PathBuf::from("/tmp/session.lock")
}

// ------------------------------------------------------------------ edge-case

pub fn load_config() -> String {
    // WAYPOINT-PLANT: waypoint-rust-env-var-unwrap
    std::env::var("DATABASE_URL").unwrap()
}

pub fn load_secret() -> String {
    // WAYPOINT-PLANT: waypoint-rust-env-var-unwrap
    env::var("API_SECRET").expect("API_SECRET must be set")
}

pub fn load_config_safe() -> String {
    // WAYPOINT-OK: falls back to a default instead of panicking
    env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite://local.db".to_string())
}

pub fn take_lock(m: &Mutex<u32>) -> u32 {
    // WAYPOINT-PLANT: waypoint-rust-lock-expect-panic
    *m.lock().expect("lock poisoned")
}

pub fn take_lock_unwrap(m: &Mutex<u32>) -> u32 {
    // WAYPOINT-PLANT: waypoint-rust-lock-expect-panic
    *m.lock().unwrap()
}

// ----------------------------------------------------------------- concurrency

pub fn unbounded_pipeline() {
    // WAYPOINT-PLANT: waypoint-rust-unbounded-channel-near-spawn
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        for i in 0..1_000_000 {
            tx.send(i).unwrap();
        }
    });
    for _ in rx {}
}

pub fn bounded_pipeline() {
    // WAYPOINT-OK: bounded channel provides backpressure
    let (tx, rx) = mpsc::sync_channel(16);
    thread::spawn(move || {
        for i in 0..1_000_000 {
            tx.send(i).unwrap();
        }
    });
    for _ in rx {}
}

pub fn shared_refcell() -> Arc<RefCell<u32>> {
    // WAYPOINT-PLANT: waypoint-rust-arc-refcell
    Arc::new(RefCell::new(0))
}

pub fn shared_mutex() -> Arc<Mutex<u32>> {
    // WAYPOINT-OK: Mutex is Sync, safe to share across threads
    Arc::new(Mutex::new(0))
}

// ---------------------------------------------------------------------- abuse

pub fn walk_depth(node: &Node, acc: &mut Vec<u32>) {
    // WAYPOINT-PLANT: waypoint-rust-unbounded-recursion
    acc.push(node.value);
    for child in &node.children {
        walk_depth(child, acc);
    }
}

pub struct Node {
    pub value: u32,
    pub children: Vec<Node>,
}
