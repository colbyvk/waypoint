# RAPTOR integration (OPTIONAL external harness — spec §8)

> **Waypoint needs no API key and no external harness.** The agent that runs Waypoint
> (or you) verifies the beacons. RAPTOR is a *purely optional* upgrade for unattended
> setups with no agent present; RAPTOR — not Waypoint — is what would use a key.

Waypoint's spec prefers **wrapping an existing agent harness over building one**.
[RAPTOR](https://github.com/gadievron/raptor) already implements almost exactly
this architecture: it maps entry points / trust boundaries / sinks, runs Semgrep
and CodeQL, dedups findings, turns unchecked flows into candidate SARIF beacons,
checks CodeQL path satisfiability before spending an LLM call, and dispatches
each finding to an agent for validation. It runs as a Claude Code harness.

This directory holds the **integration glue**, not RAPTOR itself.

## Why the fallback runs by default

`../fallback_dispatcher.py` is fully functional and is what runs out of the box,
because it needs nothing external. RAPTOR is the upgrade path when you want its
richer boundary/sink mapping and CodeQL path-satisfiability gating. Both consume
the **same** `reports/ranked.sarif` — adopting one over the other changes no
upstream stage.

## Build order (from the spec)

1. **Stand up RAPTOR against one repo.** See how far its out-of-the-box dispatch
   gets on Python and TypeScript.
   ```bash
   git clone https://github.com/gadievron/raptor && cd raptor
   # follow its README to configure the Claude Code harness + API key
   ```
2. **Identify the gaps.** They are exactly Waypoint's reason to exist: **Rust
   coverage** and the **concurrency-proxy beacons**. RAPTOR leans on Semgrep +
   CodeQL, which under-serve both.
3. **Feed Waypoint's custom beacons into the same dispatch path.** Waypoint already
   emits standard SARIF that includes the concurrency-proxy beacons and house
   rules. Point RAPTOR at `reports/ranked.sarif` (see `raptor.config.yaml` here)
   so those regions get the same situated agent visit as RAPTOR's own findings —
   closing the Rust/concurrency gap without RAPTOR needing to learn them.

## Contract between the two

- Waypoint produces `reports/ranked.sarif`: deduped, multi-tagged, ranked beacons
  with `properties.waypoint.{axes,hypothesis,content_hash,score,rank}`.
- RAPTOR consumes beacons and emits verdicts. Map each verdict back to the beacon's
  `content_hash` and append dismissals to `../../suppression/store.json` using:
  ```bash
  ../../.venv/bin/python ../fallback_dispatcher.py --record <raptor_verdicts.json>
  ```
  (The `--record` path expects a list of `{content_hash, verdict, rule_id, file,
  reasoning}` objects — the same shape the fallback writes — so the suppression
  memory is shared regardless of which harness produced the verdict.)

## Keep prompts verifier-shaped

Whether RAPTOR or the fallback drives it, the agent must stay a **verifier**:
"here is a hypothesis, here is the code, prove or disprove." Never an explorer
("find bugs in this repo"). The beacon's `hypothesis` is the framing; the context
envelope (region + immediate callers/callees) is the evidence.
