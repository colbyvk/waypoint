# Thread/task spawn or shared Arc present (Rust)

- **Axes:** concurrency
- **Languages:** Rust
- **Generated rule(s):** `waypoint-rust-concurrency-primitive`
- **Agent hypothesis:** "spawn/Arc present — unsynchronized shared-state access nearby?"

## What it is
A low-key "beacon" rule, like its Python cousin. It simply notices that the code
starts parallel work or shares ownership across it: `std::thread::spawn`,
`tokio::spawn`, or an `Arc::new(Mutex::new(...))` / `Arc::new(RwLock::new(...))`.
None of these is a problem on its own — Rust's types make most concurrency safe by
construction. The flag exists so the agent knows "parallel work happens here" and
can check whether anything shared is reached without the right synchronization. It
is a pure proxy: most matches are fine.

## Bad (flagged)
```rust
// samples/monorepo/rust_service/src/state.rs
let total = Arc::new(Mutex::new(0u64));   // shared Arc<Mutex> present
for _ in 0..8 {
    let t = Arc::clone(&total);
    let h = thread::spawn(move || {        // spawn present
        let mut g = t.lock().unwrap();
        *g += 1;
    });
    handles.push(h);
}
```

## Acceptable (not a problem)
```rust
// In the SAME sample, the spawned closure is correctly synchronized:
// samples/monorepo/rust_service/src/state.rs (WAYPOINT-OK on the lock line)
let h = thread::spawn(move || {
    let mut g = t.lock().unwrap();   // shared state touched only under the lock
    *g += 1;
});
```

## Notes for the agent
- This rule fires on the *primitive itself*, by design. The Bad and Acceptable
  snippets above are literally the same lines — the difference is whether the
  shared access inside is correctly locked, which is the agent's call to make.
- **Confirms a real concern:** shared data is read/written inside the spawned work
  without going through the `Mutex`/`RwLock`, or a lock is held across an `.await`.
- **Dismisses it:** every touch of the shared value goes through its lock, or each
  task owns its own data and only its return value is collected.
