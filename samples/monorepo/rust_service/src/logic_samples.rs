// Logic-smell fixtures (Rust) — WAYPOINT-PLANT fires, WAYPOINT-OK must not.
#![allow(unused)]

fn selfcmp(a: i32, b: i32) -> bool {
    // WAYPOINT-PLANT: waypoint-rust-logic-self-comparison
    if a == a {
        return true;
    }
    // WAYPOINT-OK: distinct operands
    a == b
}

fn boolcmp(flag: bool) -> bool {
    // WAYPOINT-PLANT: waypoint-rust-logic-bool-literal-compare
    if flag == true {
        return true;
    }
    // WAYPOINT-OK: use the bool directly
    flag
}
