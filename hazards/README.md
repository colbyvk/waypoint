# Waypoint Hazard Catalog

This folder is the **plain-English source of truth** for Waypoint's detection rules.
Each file in this directory describes one *hazard* — a code shape worth an agent's
attention — in language a domain expert can read, paired with one **bad** example
(the shape we want to catch) and one **acceptable** example (the safe lookalike we
must not nag about). The Semgrep rules under `infra/<language>/<classifier>/` are
*generated from* these descriptions, not the other way around. If a rule and a
hazard file ever disagree, the hazard file wins and the rule gets fixed.

## How to add or change a hazard (the workflow)

1. **Describe it here, in plain English.** Copy an existing hazard file as a
   template. Give it a kebab-case id (that becomes the filename), a human title,
   the axes it belongs to, and a short "What it is" paragraph. Stress *what the
   shape looks like* and *why it deserves a second look* — not how to detect it.
2. **Add a bad and an acceptable example.** The bad example is the real shape we
   want flagged. The acceptable example is the close-but-fine version we must
   leave alone. Prefer real snippets from the sample monorepo under
   `samples/monorepo/` (its `MANIFEST.md` maps every planted shape to a file and
   line, and the `WAYPOINT-OK:` comments mark the safe controls).
3. **An agent writes the matching Semgrep rule** in
   `infra/<language>/<classifier>/` — language first (`python/`, `react/`,
   `rust/`, `typescript/`), then classifier (`concurrency/`, `security/`,
   `abuse/`, `edge-case/`).
4. **Validate it.** The rule must *fire on the bad example* and *stay silent on
   the acceptable one*. The sample monorepo plus its manifest are the fixture for
   this check. A hazard isn't "done" until both halves pass.

## The four axes

Every hazard is tagged with one or more axes. They describe *what kind of trouble*
the shape points at, and they drive how findings are routed and prioritised.

- **concurrency** — shared state touched from more than one thread, task, or
  render, where ordering or interleaving can corrupt data or cause a hang.
- **security** — a path where untrusted input could reach something dangerous:
  code execution, a database query, a file, a network call.
- **abuse** — asymmetric cost: a small, cheap input that forces a large, expensive
  amount of work (ReDoS, unbounded recursion), or access shapes that let one user
  reach another user's data (IDOR).
- **edge-case** — correctness gaps that bite on the unhappy path: swallowed
  errors, missing-value dereferences, unwraps that can panic.

## These are PROXY rules — recall over precision

Read this twice. Waypoint's rules **do not claim a bug exists.** They flag a
*region worth checking*. A rule is allowed — even expected — to fire on code that
turns out to be perfectly fine, as long as it reliably fires whenever the hazard
shape is present.

In other words, each rule is tuned for **recall of the hazard-present region, not
precision about bugs.** Missing a real hazard (a false negative) is the expensive
mistake; flagging a region that turns out clean (a false positive) is cheap,
because **the agent makes the bug call, not the rule.** The cheap pattern-match
narrows the codebase down to the handful of regions where the situated judgment —
"is untrusted input actually reachable here?", "is this state really shared?" — is
worth spending. That judgment is exactly what a flat pattern match cannot do, and
it lives in the agent, guided by the "Notes for the agent" section of each hazard
file.
