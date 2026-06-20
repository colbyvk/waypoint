# rust / abuse

No custom Semgrep abuse rule lives here yet. Rust abuse signals come mainly from
off-the-shelf tools:
- **cargo-audit** — RustSec advisories, including DoS-class crates (tagged
  `security` via `tag_map.yaml`; many DoS advisories are abuse-adjacent).
- **Clippy** — `clippy::integer_arithmetic` (unchecked arithmetic on
  attacker-sized input) is tagged `abuse` in `tag_map.yaml`.

Add a rule here when you can express a Rust-specific abuse shape as a Semgrep
pattern (e.g. unbounded `Vec::with_capacity(user_input)` or input-controlled
recursion). Describe it first in `../../../hazards/`.
