// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.

pub mod state;
pub mod exec;

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// WAYPOINT-PLANT: RUST-UNWRAP [axes: edge-case]
pub fn parse_port(s: &str) -> u16 {
    s.parse::<u16>().unwrap()
}

// WAYPOINT-OK: returns Result instead of unwrapping
pub fn parse_port_safe(s: &str) -> Result<u16, std::num::ParseIntError> {
    s.parse::<u16>()
}
