// Taint-flow fixtures (Rust) — WAYPOINT-PLANT should fire, WAYPOINT-OK must not.
#![allow(unused)]
use std::process::Command;

fn command() {
    let host = std::env::var("HOST").unwrap();
    // WAYPOINT-PLANT: waypoint-rust-taint-command
    Command::new("sh").arg("-c").arg(host);
    // WAYPOINT-OK: constant argument
    Command::new("ls").arg("-la");
}

fn sql(conn: &Conn) {
    let name = std::env::var("NAME").unwrap();
    // WAYPOINT-PLANT: waypoint-rust-taint-sql
    conn.execute(name);
    // WAYPOINT-OK: constant query
    conn.execute("SELECT 1");
}
