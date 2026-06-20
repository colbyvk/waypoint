# Contributing to Waypoint

Thanks for looking. Waypoint is a small, opinionated triage engine — the bar for
changes is "keeps the custom surface tiny and the tests green."

## Philosophy (please read before adding code)
- **Assemble, don't build.** Parsing, scanning, taint, fuzzing → mature OSS tools.
  The custom surface is a few readable Python scripts + a folder of Semgrep rules.
- **Beacons, not diagnostics.** The cheap pass is *recall-biased on purpose*; output
  is deduped, ranked, suppressible, and agent-verified. Don't optimize a rule for
  precision in isolation — that's the ranker's and the agent's job.
- **The dark zone is first-class.** "No beacon" must never silently mean "safe."
- **Read-only.** Waypoint never edits the scanned code.

## Dev setup
```bash
detectors/install.sh        # core scanners into .venv (add --eslint / --all)
bin/waypoint --doctor       # confirm what's active
bin/waypoint --test         # the suite (no external scanner needed)
```

## Adding a detector rule
1. Drop a Semgrep YAML under `infra/<language>/<axis>/` (axes: security · edge-case ·
   concurrency · abuse · logic). Set `metadata.waypoint_axes` and a
   `metadata.waypoint_hypothesis` (the claim the agent will prove/disprove).
2. For a **third-party tool** rule (ruff/bandit/clippy/…), route its id to an axis in
   `tag_map.yaml` instead.
3. Validate: `.venv/bin/semgrep --validate --config infra` (must be 0 errors).
4. Add a fixture under `samples/` (mark `WAYPOINT-PLANT` = should fire,
   `WAYPOINT-OK` = must stay quiet) and a test.

### Rule-authoring lesson (learned the hard way — see hardening/RESULTS.md)
**Bare/broad patterns over-fire on real code.** `$X.decode()` matched `TextDecoder`;
`$V = $E` matched every local; `getattr(o, "x")` is static, not dynamic. Always:
constrain metavariables (`metavariable-regex`), scope by file type (`paths:` /
`--include`), prefer exact matches, and exclude string-literal forms. Then **dogfood
it on a real repo** before committing — that's how all four of those were caught.

## Tests
`tests/` exercises Waypoint's own Python (sariflib, merge, rank, coverage, dispatch,
MCP) using crafted SARIF + tiny temp trees — no external scanner required, by design.
Add a test for any new behavior. `bin/waypoint --test` must pass; CI (`.github/
workflows/ci.yml`) runs it on fresh Ubuntu + macOS from a cold install.

## Security
Scanning untrusted code must not compromise the host. Never run the *target's* eslint/
mypy config or binaries; dynamic lanes (`--deep`/`--logic`) execute target code and are
gated behind trust. See [SECURITY.md](SECURITY.md) before touching `detectors/` or `bin/`.

## Pull requests
Keep the custom surface small, keep CI green, and include a fixture + test. For
detector changes, paste before/after beacon counts on a real repo in the PR.
