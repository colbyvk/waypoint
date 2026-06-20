# What Waypoint guarantees (and what it does not)

Most scanners never state their guarantee class. Waypoint does — strongest first.

**The honest ceiling:** general *"this code has no vulnerabilities"* soundness is
**undecidable** (Rice's theorem). We do **not** claim it, ever. Here is what we *do*.

## 1. Coverage partition — SOUND, by construction
Every enumerated function is classified into **exactly one** of:
- **ANALYZED** — its body was parsed **and** it is reachable from a trust-boundary
  entrypoint via **resolved** calls.
- **DARK** — everything else: an orphan, a function reachable only via an
  unresolved/computed edge, or one in a parse-incomplete region.

`analyzed ∪ dark = all enumerated functions` and `analyzed ∩ dark = ∅`, **asserted
at runtime on every scan** (`summary.partition_holds`). The call graph is
**conservative**: an unresolved, computed, or un-boundable edge is **never** used to
mark a target reachable — we always err toward **DARK**. So no function is silently
assumed analyzed-and-safe; **the dark zone is the provable complement of what we
checked, not a guess at it.**

Scope of *enumeration* soundness:
- **Python** — via stdlib `ast`: sound. A file either parses wholesale or is reported
  as `unparsed` (zero coverage); there is no silent partial parse.
- **TS / JS / TSX / JSX / Rust** — via **tree-sitter** (real grammars) when installed:
  sound syntactic enumeration of every definition the grammar knows (declarations,
  function expressions, arrows, methods, generators, Rust fn/impl items). A function
  whose subtree contains an `ERROR`/`MISSING` node is flagged `parse-incomplete`
  (dark) with its callees dropped; a file with any parse error is flagged so a
  possibly-hidden function is accounted for as dark — never silently absent. If
  tree-sitter is **not** installed, the call graph falls back to a **conservative
  regex** extractor (errs dark, but not provably complete); `bin/waypoint --doctor`
  reports which backend is active. *Edges are name-based, not type-resolved* (`o.m()`
  → callee `m`), and Rust macro-generated code is invisible without expansion →
  conservatively dark. Those are the next frontier (type-resolved edges), not this rung.

## 2. Per-property taint — SOUND *modulo assumptions*
**Intra-file:** Semgrep **taint-mode** rules (`infra/core/<lang>/security/*-taint.yaml`)
prove attacker-source → dangerous-sink flows within a function, with sanitizers
cutting the flow — free, always-on. **Cross-file:** `--deep` / `--codeql` runs CodeQL
cross-file taint. Both are sound **modulo their assumptions** (source/sink/sanitizer
models, configured entry points). Scoped to those properties — not general soundness.

## 3. Empirical property bounds (Door 1 — property / fuzz)
`--logic` runs property-based tests + fuzzing. A passing run means *"held over N
generated inputs,"* with a **reproducing counterexample** on failure. Tested, not
proven.

## 4. Everything else — recall-biased heuristics (explicitly labeled)
The beacon detectors (Semgrep/Bandit/Ruff/Clippy/mypy/…) are **recall-biased**: they
over-flag on purpose, then Waypoint dedups, ranks, suppresses, and agent-verifies.
**Beacons are SUSPICIONS, not proofs.** The dark-zone **tiers** order by *observed*
facts (a sink the parsed body calls; a computed dispatch) — never a fabricated
severity, and never for regions we did not traverse.

## What we explicitly do NOT claim
- **Not "no bugs."** General soundness/completeness for arbitrary properties is
  undecidable; a clean Waypoint run is not a proof of safety.
- **Not complete clike enumeration** (yet) — conservative best-effort; tree-sitter
  is the follow-on.
- **A DARK region means "we did not / could not check this," NOT "it is dangerous."**
  Severity there is unknown *by definition* — which is exactly why we refuse to grade it.
