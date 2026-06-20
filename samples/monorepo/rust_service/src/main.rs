// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
mod state;
mod exec;

fn main() {
    state::shared_increment();
    let _ = state::bump();

    // WAYPOINT-PLANT: RUST-UNWRAP [axes: edge-case]
    let cfg = std::env::var("APP_CONFIG").unwrap();
    println!("config = {}", cfg);

    let cmd = std::env::args().nth(1).unwrap_or_default();
    let out = exec::run_user_cmd(&cmd);
    println!("{}", out);

    // WAYPOINT-PLANT: RUST-UNWRAP [axes: edge-case]
    let first: Option<i32> = None;
    panic!("unreachable value: {}", first.unwrap());
}
