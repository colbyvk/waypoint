<!-- Thanks for contributing to Waypoint. Keep the custom surface small and CI green. -->

## What this changes
<!-- One or two sentences. -->

## Type
- [ ] New / changed detector rule
- [ ] Engine / pipeline (callgraph, coverage, rank, merge, dispatch)
- [ ] Docs / packaging
- [ ] Bug fix

## Checklist
- [ ] `bin/waypoint --test` passes
- [ ] `semgrep --validate --config infra/core` is clean (if rules changed)
- [ ] Added a fixture (`samples/`, `WAYPOINT-PLANT` / `WAYPOINT-OK`) and a test for new behavior
- [ ] For a detector change: pasted before/after beacon counts on a real repo below
- [ ] No secrets, no vendored third-party code, no generated artifacts committed

## Before / after (detector changes)
<!-- e.g. "requests: 360 -> 312 beacons, 0 recall loss on samples" -->
