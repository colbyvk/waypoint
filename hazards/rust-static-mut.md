# `static mut` global mutable state (Rust)

- **Axes:** concurrency, security
- **Languages:** Rust
- **Generated rule(s):** `waypoint-rust-static-mut`
- **Agent hypothesis:** "static mut accessed — any concurrent reader/writer (data race)?"

## What it is
A `static mut` is a single global variable that any code can change, and Rust does
**not** wrap it in any kind of lock. Reading or writing it requires an `unsafe`
block precisely because, if two threads touch it at once, the result is a data race
— which in Rust is undefined behavior, not just a wrong answer. The flag marks both
the declaration and any access so the agent can check whether more than one thread
can ever reach this global at the same time.

## Bad (flagged)
```rust
// samples/monorepo/rust_service/src/state.rs
static mut COUNTER: u64 = 0;          // unsynchronized global mutable state

pub fn bump() -> u64 {
    unsafe {
        COUNTER += 1;                 // racy if called from more than one thread
        COUNTER
    }
}
```

## Acceptable (not a problem)
```rust
// No WAYPOINT-OK control exists in the sample; minimal correct version below.
// An atomic global is shared AND safe — no `unsafe`, no data race.
use std::sync::atomic::{AtomicU64, Ordering};

static COUNTER: AtomicU64 = AtomicU64::new(0);

pub fn bump() -> u64 {
    COUNTER.fetch_add(1, Ordering::Relaxed) + 1
}
```

## Notes for the agent
- **Confirms a real concern:** the program is multi-threaded (spawns threads, uses
  an async runtime, or is a library others call concurrently) and this global can
  be reached from more than one of those threads.
- **Dismisses it:** the global is only ever touched from a single thread (e.g. set
  once at startup before any thread spawns, or guarded by an external lock the
  agent can see).
- The modern fix is almost always an `Atomic*` type, a `Mutex`, or `OnceLock` —
  note which would fit if recommending a change.
