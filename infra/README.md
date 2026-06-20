# infra/ — the beacon-making rules

This is where Waypoint's custom detection rules live: the [Semgrep](https://semgrep.dev)
patterns that drop **beacons** on suspicious regions. Everything else (the scanners
themselves, dependency auditors, the agent) is off-the-shelf — these rules are the
genuinely custom surface (spec §6, §13).

## Layout: language first, then classifier

```
infra/
├── python/        react/        rust/         typescript/
│   ├── concurrency/      ← async/threads/shared-state proxies (spec §6)
│   ├── security/         ← input boundary → dangerous sink (spec §3.2.1)
│   ├── abuse/            ← asymmetric cost/value: ReDoS, IDOR, amplification (§3.2.4)
│   └── edge-case/        ← dropped errors, unwrap/panic, swallowed exceptions (§3.2.2)
```

Every `<language>/<classifier>/` folder holds the rules that make beacons of that
**classifier** (axis) for that **language**. A folder with a `README.md` instead
of a `.yaml` means that axis is covered for that language by an off-the-shelf tool
(noted in the README) rather than a custom rule.

Semgrep applies each rule's own `languages:` field, so the folder a rule lives in
is purely organizational — `--config infra` loads them all and each still matches
only its language's files. React rules use `languages: [typescript]` (this Semgrep
parses `.tsx`/JSX) and target React-hook/JSX shapes; language-general TS shapes
live under `typescript/`.

## These are PROXY detectors, not bug finders

A concurrency rule does not claim a race exists — static analysis cannot prove
that. It flags a *region worth an agent's attention*. Tune for **recall of the
hazard-present region**, not precision about bugs; the agent decides whether a bug
is real. False positives are cheap (the agent dismisses them and the dismissal is
remembered in `../suppression/`).

## Every rule carries its Waypoint metadata

```yaml
metadata:
  waypoint_axes: [concurrency, abuse]          # one or more of the four classifiers
  waypoint_hypothesis: "…framed question for the agent…"
  # optional: waypoint_severity_prior: 0.9 ; waypoint_subtags: [redos]
```

`../detectors/normalize/semgrep_to_sarif.py` carries these onto each beacon (Semgrep's
own SARIF exporter drops them). Off-the-shelf rule ids (Bandit `B608`, Clippy
`clippy::unwrap_used`, …) get their axes from `../tag_map.yaml` instead.

## Adding a rule (catalog-driven)

1. Describe the hazard in plain English in `../hazards/` with one **bad** and one
   **acceptable** example — that catalog is the source of truth.
2. Add the Semgrep rule under `infra/<language>/<classifier>/`, with
   `waypoint_axes` + `waypoint_hypothesis`.
3. Validate it fires on the bad example and not the acceptable one:
   ```bash
   ../.venv/bin/semgrep --validate --config infra/<lang>/<classifier>/<file>.yaml
   ../.venv/bin/semgrep --config infra ../samples/monorepo --json | less
   ```

## Gotchas (learned building these)

- This Semgrep has no `tsx` language id — use `languages: [typescript]` (it parses
  `.tsx`/JSX fine).
- Quote patterns containing `:` — e.g. Rust `"static mut $N: $T = $E;"`, JSX
  `"dangerouslySetInnerHTML={{__html: $X}}"`.
- A bare JSX attribute is not a valid pattern; wrap it in an element:
  `"<$EL dangerouslySetInnerHTML={{__html: $X}} />"`.
- Arrow-function params use `(...)`, not `($$$)`.
