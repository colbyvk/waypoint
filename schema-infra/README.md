# schema-infra — the beacon schema, one document per beacon

This directory is the **canonical schema for beacons**. A beacon is the unit
Waypoint passes downstream: "an agent should look here, and here is why." This
README defines the shared schema; the per-beacon docs under
`schema-infra/<language>/<classifier>/<rule-id>.md` (and `off-the-shelf/<tool>.md`)
each document one beacon type — **what it is, where the detection code lives, and
which linter(s) raise it**.

> These docs are **generated** from the rules themselves by
> `detectors/gen_schema_infra.py` (reads `infra/**/*.yaml` + `tag_map.yaml`), so
> "where the code lives" and "which linter fires" never drift from reality.
> Regenerate after changing rules:  `python detectors/gen_schema_infra.py`

---

## A beacon IS a SARIF 2.1.0 `result` — there is no custom schema

Waypoint invents no beacon format. Every beacon is a SARIF `result` object, which
already carries location + rule id + severity (`level`) + message. Waypoint's
extra fields live under `properties.waypoint`. One beacon, fully populated:

```jsonc
{
  "ruleId": "waypoint-py-sql-string-build",        // which detector fired
  "level":  "error",                                // SARIF: error|warning|note|none
  "message": { "text": "SQL built by string interpolation reaches execute()…" },
  "locations": [{
    "physicalLocation": {
      "artifactLocation": { "uri": "py_service/db.py" },   // repo-relative
      "region": { "startLine": 17, "endLine": 17 }
    }
  }],
  "properties": {
    "waypoint": {
      "axes":            ["security", "abuse"],     // 1+ of the four axes
      "subtags":         [],                         // free-form extra tags
      "severity_prior":  0.9,                         // 0..1, the cheap pre-agent guess
      "hypothesis":      "string-built SQL into execute() — injection if input is untrusted?",
      "content_hash":    "ca757c379a…",              // hash of the normalized region (suppression key)
      "tool":            "semgrep",                  // source detector (or "waypoint-merged")
      "rule_id":         "waypoint-py-sql-string-build",
      "merged_from":     [                            // provenance after dedup
        {"tool":"semgrep","rule_id":"waypoint-py-sql-string-build","level":"error","message":"…"},
        {"tool":"bandit", "rule_id":"B608","level":"error","message":"…"}
      ],
      "score":              1.42,                     // set by rank.py (§7)
      "rank":               1,
      "dispatch_candidate": true,                     // within the top-N budget
      "boundary_reachable": true,                     // reachable from an input/trust boundary
      "centrality":         { "caller_count": 1, "normalized": 0.5 },
      "suppressed":         null                      // {by, verdict|justification, expiry, note} when suppressed
    }
  }
}
```

## Field reference (`properties.waypoint`)

| field | type | set by | meaning |
|---|---|---|---|
| `axes` | string[] | merge | one or more of `security`, `edge-case`, `concurrency`, `abuse` |
| `subtags` | string[] | merge | non-canonical extra tags carried from a rule |
| `severity_prior` | number 0–1 | merge | the detector's cheap guess **before** any agent looks |
| `hypothesis` | string | merge | the one-line question handed to the verifier agent |
| `content_hash` | string | merge | sha256 of the **normalized region text** — the suppression key (line-drift-stable) |
| `tool` | string | merge | source detector name, or `waypoint-merged` for a deduped beacon |
| `rule_id` | string | merge | the detector rule that fired |
| `merged_from` | object[] | merge | every `{tool, rule_id, level, message}` that contributed to this region |
| `score` | number | rank | `prior + multi_axis_bonus + centrality·callers + boundary_bonus` (§7) |
| `rank` | int | rank | 1-based position after sorting by score |
| `dispatch_candidate` | bool | rank | whether it falls within the top-N agent budget |
| `boundary_reachable` | bool | rank | region is reachable from an input/trust boundary |
| `centrality` | object | rank | `{caller_count, normalized}` — approximate call-graph centrality |
| `suppressed` | object\|null | rank | set when a store/allowlist entry suppressed this beacon |

The SARIF `level` ↔ `severity_prior` mapping and all scoring weights live in
`waypoint.config.yaml`. The field semantics are implemented in
`detectors/sariflib.py` (the single source of truth for reading/writing beacons).

## The axes

The five general-software axes:

- **security** — input boundary reaching a dangerous sink (injection, exec/eval, path, TLS off, secrets, IaC exposure).
- **edge-case** — dropped errors, `unwrap`/`panic`, bare `except`, optional-deref, leaked resources.
- **concurrency** — *regions that obviously involve concurrency*; the agent decides if a race exists (proxy approach).
- **abuse** — asymmetric cost/value: ReDoS, input-driven allocation/recursion, IDOR, idempotency gaps.
- **logic** — *dynamic* evidence of a software-logic bug (not a static smell): a surviving mutant (untested/incorrect branch), a runtime data race, or a fuzz-found crash. Produced by the logic lane (`detectors/run_logic.sh`), which merges that evidence onto the same regions the static rules flag.

A beacon is **multi-tagged**; multi-axis regions score higher (the strongest cheap signal of a real problem) — e.g. a string-built SQL query tags `[security, abuse]`, and a runtime race on a region a static rule already flagged tags `[concurrency, logic]`.

## How this directory is laid out

```
schema-infra/
├── README.md                       # this file — the shared schema
├── INDEX.md                        # every beacon, grouped by language × axis (generated)
├── <language>/<classifier>/<rule-id>.md   # one doc per CUSTOM (Semgrep) beacon   (generated)
└── off-the-shelf/<tool>.md         # beacons contributed by each wired tool       (generated)
```

Each per-beacon doc states: the beacon's axes/severity/hypothesis, **where the
detection code lives** (the `infra/…` rule file, or the wired tool), **which
linter(s) raise it** (the primary Semgrep rule plus any off-the-shelf detector
that flags the same shape), the exact SARIF fields the beacon carries, and a
bad/acceptable example. That is what makes each one a *proper beacon*: enough for a
maintainer — or an agent — to know what fired, why, and where to look.
