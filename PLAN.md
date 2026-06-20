# Waypoint — Build Plan & Goal

> This document is the plan built out from [WAYPOINT_BUILD_SPEC.md](../WAYPOINT_BUILD_SPEC.md).
> It states the goal, decomposes the spec into phases and tasks with status, maps
> each to the spec, and records how completion was verified. It is the running
> checklist for the `/loop`-until-done execution of this build.

---

## Goal (the one sentence this run is judged against)

**Build the entire Waypoint system from the spec — a *command* you point at any
directory that runs a cheap deterministic pass (off-the-shelf scanners + custom
Semgrep rules) to drop SARIF "beacons", merges/tags/dedups/ranks/suppresses them,
and dispatches the top ones to a verifier agent — honoring "assemble, don't
build" (tiny custom surface), passing every §14 acceptance criterion, and
verified end-to-end against a polyglot fixture — then stop.**

Done = `bin/waypoint <dir>` runs clean across all four languages, the full test
suite passes, and all §14 acceptance criteria hold, with no remaining gaps.

---

## Door 1 (the correctness lane) — COMPLETE [x]

Closed the correctness/logic gap with the remaining **spec-free, no-agent**
detectors. Property-based testing + 4-language fuzzing shipped earlier; the three
remaining levers are now done, all pure detectability (agent/dispatch untouched):

1. **Logic-smell static rules** [x] — 14 net-new Semgrep rules in `infra/<lang>/logic/`
   (Python 5, TypeScript 5, Rust 2, React 2): self-comparison, `is`-vs-`==` on
   literals, return-in-finally, constant condition, `== None`, assignment-in-
   condition, `Array.sort()` w/o comparator, NaN comparison, conditional React
   hooks, `useEffect` with no deps. **`logic` is now a static axis** (logic beacons
   appear on the plain scan, not only `--logic`). All fire on plants, quiet on OK.
2. **Strict-type / exhaustiveness amplifiers** [x] — cranked the type-checkers that
   prove what patterns can't: **mypy** `--warn-unreachable --strict-equality
   --warn-no-return` (→ `[unreachable]`/`[comparison-overlap]`/`[return]`) and
   **clippy** correctness/suspicious (`eq_op`, `ifs_same_cond`, `almost_swapped`,
   …), both routed to the `logic` axis via `tag_map.yaml`. TS/React correctness is
   delivered by the pillar-1 Semgrep rules (no redundant eslint cranking).
3. **Differential / metamorphic** [x] — the property lane now generates relation
   tests (Hypothesis ghostwriter `--roundtrip/--idempotent/--equivalent/--binary-op`
   via `logic.property_relations`) and **labels** a falsified relation on the beacon
   (subtag `roundtrip`/`idempotent`/`differential`/`commutative`/`metamorphic`).

Verified: `semgrep --validate` → **176 rules, 0 errors, 0 dupes**; **81/81 tests**;
`bin/waypoint samples/monorepo` clean with **logic=18** on the plain scan;
mypy correctness findings confirmed `logic`-tagged; a falsified roundtrip renders
as `logic — roundtrip` with its reproducing input. **Agent/dispatch layer untouched.**

---

## Detection-gap closure (the 8/10 routing/coverage fixes) — COMPLETE [x]

Closed the four gaps from the agent-routing rating, all detection/ranking-side
(agent/dispatch untouched):

1. **Cross-file / interprocedural** [x] — CodeQL is now a first-class OPT-IN lane
   ([detectors/run_codeql.sh](detectors/run_codeql.sh)) with a one-shot command:
   `bin/waypoint <dir> --codeql`, or `--all` (every detector + logic lane + CodeQL).
   Per-language DB build + security-extended suite → native SARIF that merges like any
   beacon; skips with an install hint when the CLI is absent (live run needs the CLI, §15.3).
2. **Heuristic ranking → real call graph** [x] — [prioritise/callgraph.py](prioritise/callgraph.py)
   builds caller→callee edges (Python via `ast`; TS/Rust via a brace-scoped extractor) and
   gives `rank.py` **proven reachability** (BFS from trust-boundary entrypoints) + **fan-in
   centrality**. Beacons carry `boundary_source: call-graph|heuristic`; on the sample 289/387
   use graph fan-in and 16 are proven-reachable. Text/glob heuristic kept as a fallback.
3. **Precision calibration** [x] — [prioritise/calibration.py](prioritise/calibration.py) turns
   past agent verdicts (confirm/dismiss per rule) into a per-rule precision and a score
   multiplier, so chronically-dismissed rules sink and confirmed ones rise. Neutral until
   history exists; `bin/waypoint <dir> --calibrate` recomputes it.
4. **Auth / access-control pack** [x] — 6 net-new OWASP-A01 rules (`infra/<lang>/authz/`):
   unauthenticated Flask route, mass-assignment over-binding, privilege-from-request
   (Python + TS), client-side-only auth guard (React). 14 authz beacons on the sample.

Verified: **176 rules (0 errors/dupes), 81 tests**, full pipeline clean (security 225,
abuse 102, logic 18), call graph + calibration exercised end-to-end.

---

## Tiered engine + incremental scanning — COMPLETE [x]

Made the single deterministic CLI (`bin/waypoint`) explicitly **tiered** so it
"mass-finds in seconds, cheaply" by default, with heavier analysis opt-in:

- **Fast tier (default, `--fast`)** — deterministic scanners + 176 rules, no agent,
  no CodeQL: seconds, $0. This is the mass-find path.
- **`--changed` / `--since REF`** — incremental: scans only files changed vs git,
  then splices a per-target **cached baseline** (`reports/_work/baseline-*.sarif`)
  for unchanged files, so a seconds-long re-scan still shows the full picture.
  Repo/crate/manifest scanners skip in changed-mode; graceful full-scan fallback
  when the target isn't a git repo or has no baseline yet (`prioritise/incremental.py`).
- **`--deep` (= `--codeql --logic`)** — CodeQL cross-file taint + the dynamic logic
  lane. Minutes; nightly / on-demand.
- **`--dispatch`** — the agent verifies the **top-N** ranked beacons. The agent is
  NEVER in the mass-scan path; the deterministic CLI owns all tool orchestration.

Plus `detectors/install_codeql.sh` (one-command CodeQL bundle install) and a CodeQL
SARIF **ingestion test** (cross-file dataflow → security+abuse beacon), so the deep
tier's only remaining prereq is running that installer. The agent skill was
tightened to default to the fast tier and verify-only.

Verified: full mode unchanged (454 semgrep findings); `--changed` live in a git repo
scopes to the changed files (454 → 8) and splices the baseline (6 fresh + 11 cached
→ 12 combined); **81 tests**; all four entrypoints `bash -n` clean.

---

## Security hardening for open-source (review Phase 1 + 2) — COMPLETE [x]

Pre-release hardening against Waypoint's own threat model (it scans untrusted code):

- **1A — fast tier can't execute target config.** mypy `--config-file=infra/mypy/waypoint.cfg`
  (blocks a malicious `mypy.ini` `plugins=` — verified vuln→fix); ESLint is Waypoint-owned +
  `--no-config-lookup` + `infra/eslint/waypoint.eslint.config.mjs` (never the target's binary/config/plugins).
- **1B — dynamic lanes gated + sandboxed.** `--logic/--deep` refuse unless `--i-trust-this-code`
  / `WAYPOINT_TRUSTED=1` (verified; `run_logic.sh` self-guards). `bin/waypoint-sandboxed` + `Dockerfile`
  run in a no-network, read-only, non-root, ephemeral container (built; live run needs a docker daemon).
- **2 — CodeQL download verified.** `install_codeql.sh` pins `codeql-bundle-v2.25.6`, fail-closed
  SHA-256 (pinned osx64 + `gh attestation` + `WAYPOINT_CODEQL_SHA256`), `tar --no-same-owner`.
- **3 — .gitignore** adds `.codeql/` + `suppression/calibration.json`.
- **4 — secret redaction.** `sariflib.redact_secrets()` + `emit_beacons.py` mask secret values in
  beacon `.md`; INDEX sensitivity warning (verified — a planted AWS key is never written out).

Verified: **84 tests**, 176 rules (0 errors), full fast scan clean (400 beacons), all entrypoints `bash -n`.

**Phase 3–5 (defense-in-depth · supply chain · OSS process) — COMPLETE [x]:**
- #5 `resolve_path` clamped to the scanned tree (realpath; blocks `..` + symlink-out — tested).
- #7 changed-file handling NUL-safe end to end (verified a `a b.py` filename scopes correctly).
- #11 `--since` ref validated (`rev-parse --verify "$REF^{commit}"`, reject leading `-` — `--since --evil` rejected).
- #6 deps pinned — `requirements.txt` (`==`), `install.sh -r`, `cargo install --locked`, committed `package.json` + `package-lock.json` (`npm ci`).
- #8 `SECURITY.md` + a README "Security & threat model" section.  #9 `LICENSE` = **Apache-2.0**.  #10 `samples/README.md` ("intentionally insecure") + `.github/codeql/codeql-config.yml` (`paths-ignore: samples/**`).

The full open-source security review (Phases 1–5) is now complete; the only runtime caveat is the Docker sandbox needs a live daemon.

---

## What the spec asks for (my reading of WAYPOINT_BUILD_SPEC.md)

Read in full before building. The non-obvious constraints that shaped every
decision below:

- **It is NOT a linter.** A linter prints diagnostics for a human; Waypoint drops
  *beacons* (markers on regions worth an agent's attention) and routes them to an
  LLM agent for situated judgment. (§1)
- **The cheap pass is deliberately dumb.** It matches *shapes*, not *meaning*, and
  decides only "worth a look" — never "actually broken." Meaning is the agent's
  job. (§1)
- **Beacons ARE SARIF — invent no schema.** Every tool emits/normalizes to SARIF
  2.1.0; the extra fields (axes, prior, hypothesis, content-hash) live in
  `result.properties`. This is what lets every stage speak one language. (§2.2)
- **Assemble, don't build.** Where the spec says *install*, wire up an existing
  tool; where it says *author*, write new code. The custom surface must stay tiny
  for a non-SWE team to own. (§13)
- **Four languages** (Python, Rust, React, TypeScript) and **four axes**
  (security, edge-case, concurrency, abuse); beacons are multi-tagged and multi-axis
  regions rank higher. (§3)
- **Concurrency is handled by PROXY** — the one genuinely custom detection idea.
  Static tools can't prove a race, so flag *regions that obviously involve
  concurrency* and let the agent reason. (§6)
- **Rank to avoid drowning** (§7); **remember dismissals** via content-hash
  suppression with expiry, else the team abandons it in weeks (§9).
- **Prefer wrapping RAPTOR** as the agent harness; a thin fallback dispatcher only
  if needed. Keep agent prompts verifier-shaped, never explorer-shaped. (§8)
- **Build in phase order** 0→5, each independently useful and testable. (§11)
- **Keep "what fired" separate from "what the agent concluded"** (§2.3); flag the
  five owner decisions rather than guessing them (§15).

## Approach (from the spec)

A triage funnel: `codebase → [cheap deterministic pass drops beacons] → [rank +
dedup + suppress] → [expensive agent verifies each beacon] → findings`. The cheap
pass decides *worth an agent's attention*, not *actually broken*. Everything
hard (scanning, parsing, taint, agent orchestration) is delegated; the custom
surface is a few readable scripts + a folder of rules.

---

## Phases (do in order; each independently useful)

### Phase 0 — Skeleton & one tool [x]
- [x] Repo layout + central config — `waypoint.config.yaml`, `tag_map.yaml`
- [x] Sample polyglot monorepo fixture (Py/Rust/React/TS), 37 planted issues + 11 clean controls — `samples/monorepo/`
- [x] Semgrep running, emitting well-formed SARIF
- *Spec: §10, §11(P0)*

### Phase 1 — Collection layer (no AI, deterministic) [x]
- [x] `detectors/install.sh` (venv; PEP-668-safe), `detectors/run_all.sh` (runs every installed tool, skips missing)
- [x] SARIF normalizers — `detectors/normalize/` (semgrep, bandit, pip-audit, clippy, cargo-geiger, mypy); native SARIF for ruff/trivy/gitleaks/osv/eslint/codeql
- [x] `detectors/merge_sarif.py` — merge, tag axes + hypothesis, dedup overlapping regions, content-hash; `detectors/sariflib.py` shared lib
- *Spec: §4, §11(P1), §13*

### Phase 2 — Concurrency-proxy + house rules [x]
- [x] Custom Semgrep rules in `infra/<language>/<classifier>/` — **176 rules** across the **general-software axes** (security / edge-case / concurrency / abuse / logic) × Python / Rust / TypeScript / React, plus **20 IaC/CDK** (AWS cloud-config). Includes **14 logic-smell static rules** (`infra/<lang>/logic/`) that make `logic` a *static* axis, and **6 authz/access-control rules** (`infra/<lang>/authz/`, OWASP A01). *(Data-engineering / PIT detection was **cut per owner**.)*
- [x] **Taint-mode (dataflow) detection** — **14 rules** (Python 7, TypeScript 5, Rust 2; TS covers React `.tsx`): a beacon fires only when **untrusted input actually flows into a sink** (SQLi, command, path, SSRF, code-exec, XSS, open-redirect, deserialization, SSTI). Detects real injections shape rules miss **and** stays quiet on parametrized/sanitized/constant paths — improving both depth and signal without touching the agent.
- [x] `hazards/` plain-English catalog (source of truth, 13 docs) → rules generated from it
- [x] Validated: concurrency proxies fire on known regions in all four languages
- *Spec: §6, §11(P2), §16*

### Phase 3 — Prioritisation + suppression (no AI) [x]
- [x] `prioritise/rank.py` — `score = prior + multi_axis_bonus + centrality·callers + boundary_bonus`
- [x] `prioritise/suppress.py` + `suppression/store.json` + `suppression/allowlist.yaml` — content-hash suppression with expiry; allowlist needs justification + expiry
- *Spec: §7, §9, §11(P3)*

### Phase 4 — Agent dispatch [x]
- [x] `dispatch/fallback_dispatcher.py` — context envelope (region + callers/callees), verifier-shaped prompt, dry-run/claude-cli/anthropic-api backends, verdicts → suppression store
- [x] `dispatch/raptor/` — integration with the preferred RAPTOR harness (README + config stub)
- *Spec: §8, §11(P4)*

### Phase 5 — Entry point & CI [x]
- [x] `bin/waypoint` — the single command: point it at a directory, runs detect → merge → rank → (dispatch)
- [x] `.github/workflows/waypoint.yml` — optional CI: deterministic scan on push/PR, agent triage on a nightly schedule (runs `bin/waypoint`)
- *Spec: §11(P5), §12*

---

## Custom surface authored (the only hand-maintained code — spec §13)
- [x] SARIF normalization wrappers · [x] `merge_sarif.py` · [x] **176** Semgrep rules incl. 14 taint-mode dataflow + 14 logic-smell + 6 authz/access-control rules (general-software + IaC/CDK; data-engineering cut)
- [x] **Beacons as Markdown** — `prioritise/emit_beacons.py` writes a root-level `beacons/` dir: `beacons/INDEX.md` + `beacons/<rank>_<hash>.md` (each: **file path + classification** of the issue). Clear with `bin/wipe-beacons`. Waypoint *drops beacons*, it is not a linter.
- [x] Renamed buoys → **beacons** throughout (code, `reports/beacons.sarif`, docs, schema-infra)
- [x] **Agent skill (vendor-neutral)** — `skills/waypoint/SKILL.md`: the universal playbook any agent (Claude/Gemini/ChatGPT/Cursor) follows to run `bin/waypoint`, **verify the top beacons by reading the code**, and report in plain English. Self-bootstrapping (installs if missing); symlinked into `.claude/skills/` so Claude Code auto-discovers it.
- [x] IaC/cloud-config via Trivy misconfig (Terraform/CFN/Dockerfile/K8s) + AWS-CDK rules · [x] CodeQL cross-file taint wired + enabled
- [x] **Policy gate** — `prioritise/gate.py` + `bin/waypoint --gate`: exits non-zero when beacons violate `gate:` policy, so CI can block a PR/deploy (the "teeth")
- [x] **Software-logic lane** — `detectors/run_logic.sh` + normalizers turn dynamic evidence into `logic` beacons; `bin/waypoint --logic`, opt-in/nightly. Brings *dynamic* logic evidence onto the regions static rules flag:
  - mutation (`mutants_to_sarif`), data races (`race_to_sarif`), fuzz crashes (`fuzz_to_sarif`);
  - **property-based testing** (`hypothesis_to_sarif`, `proptest_to_sarif`, `fastcheck_to_sarif`) — Python / Rust / TypeScript+React — a falsified invariant becomes a beacon **carrying the minimal reproducing input** (`reproducing_input` + `property` in the beacon, shown in the `.md`);
  - **four-language fuzzing** — `fuzz_to_sarif` now reads cargo-fuzz (Rust), **atheris** (Python) and **jazzer.js** (TS/JS) crashes and carries the crashing input. This is the correctness lever: it finds logic bugs with **no spec and no existing tests**, the half static rules can't reach.
- [x] `rank.py` · [x] suppression store + allowlist · [x] CI glue · [x] fallback dispatcher
- [x] `bin/waypoint` command · [x] `sariflib.py` / `suppress.py` shared libs · [x] 40 tests
- [x] `schema-infra/` — beacon-schema docs (one `.md` per beacon: axes, where the code lives, which linters fire, SARIF fields, example) generated from the rules by `detectors/gen_schema_infra.py`

## Acceptance criteria (§14) — all PASS
- [x] Runs cleanly against a polyglot repo (Python, Rust, React, TypeScript)
- [x] Every detector normalized to valid SARIF 2.1.0 and merged into one beacon file
- [x] Beacons multi-tagged across four axes; carry severity prior + templated hypothesis
- [x] Concurrency-proxy rules fire on known concurrency regions in all four languages
- [x] Beacons ranked; multi-axis + boundary-reachable surface first
- [x] Dismissed beacon is content-hash-suppressed; does not re-raise until region changes / expiry
- [x] "What fired" (raw per-tool SARIF) stored separately from "what concluded" (verdicts.json)
- [x] Agent layer dispatched on a schedule; confirm/dismiss/escalate verdicts with code evidence
- [x] No component requires the team to debug a bespoke parser/scanner engine

## Decisions left to the owner (§15)
Flagged, not guessed — see [DECISIONS.md](DECISIONS.md) (repo host, model+budget, CodeQL on/off, expiry+sign-off, monorepo vs per-service).

---

## Verification (how "done" was proven)
- `bin/waypoint samples/monorepo`: 624 raw → 369 beacons (122 multi-axis) → 367 active + 2 suppressed, 7 tools, 0 SARIF validation errors.
- 176 Semgrep rules valid (`semgrep --validate --config infra` → 0 errors), 0 duplicates. Data-engineering rules removed — **only general-software domains remain**.
- Beacons span the general-software axes: security 217, edge-case 141, concurrency 64, abuse 88 (logic appears when the `--logic` lane runs).
- **Property + fuzz lane** verified end-to-end on captured tool output: a proptest counterexample flows merge → rank → emit and the dropped beacon `.md` carries `Property violated:` + `Reproducing input: x = 0, lo = 0, hi = -1`. All sub-lanes skip cleanly when their toolchain is absent.
- **Beacons as Markdown** (root `beacons/`): `beacons/INDEX.md` + `beacons/*.md` carry the **file path + classification** of every issue; `bin/wipe-beacons` clears them; an agent skill (`.claude/skills/waypoint/`) drives scan→read→triage. (`emit_beacons.py`, 2 tests.)
- General-software hardening (+30 rules): insecure tempfile, CSRF-exempt, CORS wildcard, JWT-no-verify, LDAP-fstring, TOCTOU, thread-shared-no-lock, SSRF (py/rust/ts), TLS-verify-off, decompression/entity bombs, tokens-in-web-storage, env-secret-in-bundle, … all validated + firing.
- IaC/cloud: Trivy misconfig (Terraform/CFN/Dockerfile/K8s) + 20 AWS-CDK rules → cloud-config beacons, top-ranked.
- **Policy gate**: `bin/waypoint --gate` exits 1 on violations, 0 when clean. **Logic lane**: `bin/waypoint --logic` ingests cargo-mutants/race/fuzz as `logic` beacons. **CodeQL** wired + enabled (runs when CLI present).
- `detectors/gen_schema_infra.py`: 176 beacon-schema docs + 19 wired-tool docs.
- `bin/waypoint --test`: **81/81 tests** pass (custom layer verified with no external scanner).

## Status: COMPLETE
Waypoint targets **general software domains only** (data-engineering/PIT removed per
owner). It scans Python / Rust / TypeScript / React + IaC; drops **beacons**
(renamed from "buoys") as Markdown carrying each issue's **file path + classification**;
ranks, dedups, and suppresses them; optionally dispatches the top ones to a verifier
agent; gates CI; and runs an opt-in logic lane (mutation / race / fuzz /
**property-based testing** + four-language fuzzing, with a **reproducing input**
on each logic beacon). It is a beacon-dropper, not a linter.
**176 rules (14 taint-mode + 14 logic-smell + 6 authz) · 81 tests · all green.**

### Remaining items — externally blocked, NOT open work
- **Live CodeQL run** — wired + enabled; needs the CodeQL CLI (not installable in this sandbox).
- **Live agent dispatch** — backends wired; needs an API key + per-run budget (owner, §15).
- **Per-rule precision/recall calibration** — needs the team's real repos; the fixture only proves rules fire.
