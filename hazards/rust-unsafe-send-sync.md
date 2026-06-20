# Hand-written `unsafe impl Send`/`Sync` (Rust)

- **Axes:** concurrency, security
- **Languages:** Rust
- **Generated rule(s):** `waypoint-rust-unsafe-send-sync`
- **Agent hypothesis:** "hand-written unsafe Send/Sync — is the cross-thread invariant actually sound?"

## What it is
Rust normally figures out for itself whether a type is safe to move between threads
(`Send`) or share between threads (`Sync`). A hand-written `unsafe impl Send` or
`unsafe impl Sync` is the programmer overriding that check and *promising* the type
is thread-safe — the compiler takes them at their word and verifies nothing. That
promise is exactly the kind of claim that is easy to get wrong, especially when the
type holds a raw pointer or other non-thread-safe resource. The flag marks every
such hand-written promise so the agent can check whether it actually holds.

## Bad (flagged)
```rust
// samples/monorepo/rust_service/src/state.rs
pub struct RawHandle {
    ptr: *mut u8,          // a raw pointer — not automatically thread-safe
}

unsafe impl Send for RawHandle {}   // hand-written promise the compiler can't check
unsafe impl Sync for RawHandle {}
```

## Acceptable (not a problem)
```rust
// No WAYPOINT-OK control exists in the sample; minimal correct version below.
// Let the compiler derive thread-safety from thread-safe fields instead of
// asserting it by hand. No `unsafe impl` needed.
use std::sync::Arc;

pub struct SafeHandle {
    data: Arc<Vec<u8>>,    // Arc<Vec<u8>> is already Send + Sync automatically
}
```

## Notes for the agent
- **Confirms a real concern:** the type holds a raw pointer, a non-atomic interior
  cell, an FFI handle, or anything else that is genuinely unsafe to touch from two
  threads — and the surrounding code does move/share it across threads.
- **Dismisses it:** there is a sound, documented invariant (e.g. the pointer is
  only ever accessed behind an external mutex, or the resource is provably owned by
  one thread) and a `// SAFETY:` comment explaining it.
- Either way this is a high-value beacon: an unsound `Send`/`Sync` is undefined
  behavior, not a mere bug.
