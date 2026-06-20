// Loop fixtures — WAYPOINT-PLANT should fire, WAYPOINT-OK must not.
#![allow(unused)]

fn event_loop() {
    // WAYPOINT-PLANT: waypoint-rust-infinite-loop
    loop {
        handle();
    }
}

fn spin() {
    // WAYPOINT-PLANT: waypoint-rust-infinite-loop
    while true {
        tick();
    }
}

fn bounded(items: &[i32]) {
    // WAYPOINT-OK: bounded iteration over a finite slice
    for it in items {
        process(it);
    }
}
