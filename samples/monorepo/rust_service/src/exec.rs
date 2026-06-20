// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
use std::process::Command;

pub fn run_user_cmd(user_input: &str) -> String {
    // WAYPOINT-PLANT: RUST-CMD-INJECT [axes: security]
    let out = Command::new("sh")
        .arg("-c")
        .arg(user_input)
        // WAYPOINT-PLANT: RUST-UNWRAP [axes: edge-case]
        .output()
        .expect("command failed to start");
    String::from_utf8_lossy(&out.stdout).to_string()
}

// WAYPOINT-OK: fixed argv, no shell, no user-controlled interpolation
pub fn list_dir() -> std::io::Result<std::process::Output> {
    Command::new("ls").arg("-la").output()
}
