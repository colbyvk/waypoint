---
name: waypoint
description: Scan a codebase with Waypoint and triage the results for the user. Use whenever someone wants to know whether their code is safe/correct enough to ship, asks to "harden", "review", "audit", or "secure" a repo, wants to find security / logic / concurrency / dependency / IaC issues, or asks what a recent change introduced. Works on any directory containing Python, Rust, TypeScript, or React.
---

# Waypoint — universal agent operating guide

**Who this is for:** any AI coding agent — Claude, Gemini, ChatGPT/Codex, Cursor, Windsurf, or anything else.

**The arrangement:** the human knows the *pain* ("is my app going to break or get hacked in production?"), not the *software*. **You operate Waypoint for them** and report what's actually wrong in plain English. They should never have to learn a flag, read SARIF, or understand the internals.

Waypoint is a read-only code-triage engine: a cheap, deterministic pass drops ranked **beacons** (markers on suspicious regions). Your job is to run it, **verify the top beacons yourself by reading the code**, and tell the human what's real and how to fix it.

> **The whole interface, for the human, is one sentence:** *"Use Waypoint to check this repo."* That's the entire UX — you do everything below; they never see a flag.

## Golden rules
- **Read-only on their code.** Waypoint never edits source — and neither do you, unless they ask. Everything it produces lives under `beacons/` and `reports/`.
- **Always go through `bin/waypoint`.** Never invoke semgrep / codeql / bandit / etc. directly — the CLI orchestrates every tool and ranks the results into one set.
- **You are the verifier.** Beacons are recall-tuned *suspicions*, not confirmed bugs. Open the cited file, read the region, decide real vs. false positive, and report only what you've confirmed (flag anything you're unsure about).
- **Fast tier by default.** It's seconds and free ($0, no API calls). Go deeper only when it's warranted.

## Steps
1. **Find the target** — ask which directory/repo to scan, or infer it from context.
2. **Locate Waypoint & confirm coverage** — the directory that contains `bin/waypoint`. If `.venv/` is missing, set it up **silently** once: `detectors/install.sh` (add `--eslint` if the target has TypeScript/React). Then run `bin/waypoint --doctor`: if it reports the **CORE missing**, stop and tell the human what to install; if a lane is **degraded** (e.g. `eslint [--]` on a TS repo, `codeql [--]`), note it and **disclose it in your final report** so they know coverage was partial. The setup stays invisible — but a coverage gap must never be silent.
3. **Clear old beacons:** `bin/wipe-beacons`
4. **Scan — fast tier is the default:**
   ```
   bin/waypoint "<TARGET_DIR>"
   ```
   Escalate ONLY on demand:
   - `--changed` — only files changed vs git (+ a cached baseline for the full picture). Use for *"what did my latest change introduce?"*
   - `--deep` — adds CodeQL cross-file taint + the dynamic logic lane (mutation / race / fuzz / property tests, which attach a **reproducing input**). Use for a thorough audit when minutes are acceptable. (CodeQL needs its CLI; if absent, run `detectors/install_codeql.sh` once.)
     [!] **`--deep`/`--logic` EXECUTE the target's own code**, so Waypoint refuses them unless trusted. On code the user trusts, add `--i-trust-this-code`. On **untrusted** code, run it isolated instead: `bin/waypoint-sandboxed <dir> --deep` (no-network, read-only, non-root container).
   - `--gate` — pass/fail exit code, for CI.
5. **Read the beacons** in `beacons/` — start with `beacons/INDEX.md` (the ranked table: file · classification · rule · score), then open the top per-beacon `.md` files.
6. **Check the blind-spot map** `beacons/BLINDSPOTS.md` — the "dark zone": regions Waypoint **could not analyze** (dynamic dispatch, handlers reached by a framework/reflection, files it couldn't parse), ranked by attack-surface relevance. These carry **no beacon**, so never read their silence as "safe" — open the cited region and answer the hypothesis yourself (how is it reached? can untrusted input get here? does it hit a sink?). This is where real bugs hide that the deterministic pass structurally cannot see.
7. **Verify each top beacon yourself.** Open the cited `file:line`, read the surrounding code, and judge whether it's a real problem on a reachable path. Treat the beacon's *hypothesis* as the claim to prove or disprove. Logic-lane beacons include a **reproducing input** — use it.
8. **Report in plain English.** For each *confirmed* issue: **what** it is, **where** (`file:line`), **why** it matters (what breaks in production), and **the fix**. Lead with the worst. Group by theme (security · correctness · dependencies · config). Cover both confirmed beacons *and* anything you found investigating the blind spots. Say how many suspicions you reviewed and dismissed as false positives.

## Automation & the learning loop (unattended / CI — NOT interactive triage)
When running headless — CI, a batch job, or an explicit "triage it all for me" handoff —
you can let Waypoint's own agent layer do the verifying, and let it **learn**:
- `bin/waypoint <dir> --dispatch [--backend …]` — send the top-N **beacons** to the verifier agent; writes verdicts.
- `bin/waypoint <dir> --investigate [--backend …]` — send the top-K **dark-zone** blind spots to the verifier, each with a scoped hypothesis.
- `bin/waypoint <dir> --gate` — non-zero exit if beacons violate the policy gate (CI teeth).
- `bin/waypoint <dir> --calibrate` — recompute per-rule precision from accumulated verdicts.

**The loop:** `--dispatch` / `--investigate` produce verdicts → `--calibrate` turns them into per-rule score multipliers → the next scan ranks sharper on *this* repo (rules that keep getting dismissed sink; confirmed ones rise). Backends: `dry-run` (default, $0, writes prompts), `claude-cli`, `anthropic-api`. For an interactive human, skip all of this — *you* are the verifier (see Don't).

## What it covers
Five axes — **security, edge-case, concurrency, abuse, logic** — plus dependency CVEs, secrets, and IaC / cloud-config, across **Python, Rust, TypeScript, React**. 176 custom rules + wired scanners (Semgrep, Bandit, Ruff, mypy, Clippy, Trivy, Gitleaks, pip-audit, osv-scanner, eslint), optional CodeQL cross-file taint, and a dynamic logic lane that produces reproducing inputs. Every scan also produces a **blind-spot map** (`beacons/BLINDSPOTS.md`) — the regions it *couldn't* verify — so coverage gaps are explicit, not silent.

## Don't
- Don't run the built-in agent dispatch (`--dispatch`) or `--investigate` for an interactive user — **you** are the verifier (read `INDEX.md` and `BLINDSPOTS.md` and judge them yourself). `--dispatch` (beacons) and `--investigate` (blind spots) are for unattended / CI runs and spend API budget.
- Don't dump raw SARIF or the full beacon list at the human — triage first.
- Don't edit or "fix" their code without asking.

---

### Loading this skill in each agent
This file is vendor-neutral; the canonical copy lives at **`waypoint/skills/waypoint/SKILL.md`**. Auto-discovery differs per ecosystem:
- **Claude Code:** symlinked into `.claude/skills/waypoint/` (auto-discovered).
- **Cursor / Windsurf:** reference it from `.cursor/rules` or an `AGENTS.md`.
- **Gemini / ChatGPT / others:** point the agent at this file, or paste it in, as the operating instructions.

**MCP (recommended, cross-vendor) — Waypoint ships an MCP server.** Register it via the repo's `.mcp.json`, the Claude Code plugin (`.claude-plugin/plugin.json`), or `claude mcp add waypoint -- /abs/path/to/waypoint/bin/waypoint-mcp`. Any MCP agent then calls `waypoint_doctor` / `waypoint_scan` / `waypoint_beacons` / `waypoint_dark_zone` natively — and this file is the playbook it follows after the scan (run → verify the top beacons + dark-zone gaps yourself → report).
