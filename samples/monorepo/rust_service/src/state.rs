// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
use std::sync::{Arc, Mutex};
use std::thread;

pub struct RawHandle {
    ptr: *mut u8,
}

// WAYPOINT-PLANT: RUST-UNSAFE-SEND-SYNC [axes: concurrency,security]
unsafe impl Send for RawHandle {}
// WAYPOINT-PLANT: RUST-UNSAFE-SEND-SYNC [axes: concurrency,security]
unsafe impl Sync for RawHandle {}

// WAYPOINT-PLANT: RUST-STATIC-MUT [axes: concurrency,security]
static mut COUNTER: u64 = 0;

pub fn bump() -> u64 {
    unsafe {
        // WAYPOINT-PLANT: RUST-STATIC-MUT [axes: concurrency,security]
        COUNTER += 1;
        COUNTER
    }
}

pub fn shared_increment() {
    let total = Arc::new(Mutex::new(0u64));
    let mut handles = vec![];
    for _ in 0..8 {
        let t = Arc::clone(&total);
        // WAYPOINT-PLANT: RUST-ARC-MUTEX [axes: concurrency]
        let h = thread::spawn(move || {
            // WAYPOINT-OK: properly-locked Arc<Mutex> within a clear scope
            let mut g = t.lock().unwrap();
            *g += 1;
        });
        handles.push(h);
    }
    for h in handles {
        // WAYPOINT-PLANT: RUST-UNWRAP [axes: edge-case]
        h.join().unwrap();
    }
}
