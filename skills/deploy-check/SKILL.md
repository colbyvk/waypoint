---
name: deploy-check
description: Plain-English "is my app safe to deploy?" check for non-technical / vibe-coder users. Use PROACTIVELY whenever someone is about to deploy, ship, go live, push to production, or asks "is this safe / secure / will this get hacked?" about an app they built (especially AI-generated). Runs Waypoint's deploy profile and returns a red/yellow/green verdict with a short, plain-English fix list — no security jargon, no SARIF. Works on Python, Rust, TypeScript, React.
---

# deploy-check — "am I safe to ship?" for people who don't know what CI is

**Who this is for:** someone who built an app (often with an AI agent) and is about
to deploy it. They are anxious about getting hacked or leaking data. They do **not**
know what a linter, SARIF, or CI is, and they should never have to. You do all the
work and hand them a verdict a non-engineer can act on.

**Offer it proactively.** When the user says anything like "I'm about to deploy,"
"is this safe to ship?," "will this get hacked?," "push to production," or you're
about to help them deploy — *say*: **"Want me to run a quick safety check before you
ship? Takes a few seconds and I'll tell you if anything needs fixing first."** Then run this.

## Golden rules
- **Plain English only.** No "beacon", "SARIF", "taint", "dark zone", "static analysis".
  Talk about *risks* ("anyone on the internet could read your database", "a password is
  hard-coded in your app").
- **You are the verifier.** The tool's verdict is a *starting point*, not the answer.
  Open the flagged code, confirm each issue is real, and **upgrade or downgrade the
  verdict yourself.** Never forward a raw machine verdict.
- **Free, no key, no setup for them.** It runs locally; they install nothing.

## Steps
1. **Confirm the app folder** (infer from context or ask "which folder is your app?").
2. **Set up Waypoint once if needed** (silent): if `.venv/` is missing in the Waypoint
   dir, run `detectors/install.sh`, then `bin/waypoint --doctor` — core install is
   pip-only and works on any machine with `python3`. If doctor reports the CORE missing,
   tell them the one thing to install; otherwise proceed silently.
3. **Run the deploy check:**
   ```
   bin/waypoint "<APP_DIR>" --deploy
   ```
   (Online and want broader coverage? add `SEMGREP_EXTRA="p/owasp-top-ten p/secrets"`
   before the command — it pulls curated community rules. Skip if offline.)
4. **Read the rollup** `reports/deploy_readiness.json` — it pre-sorts findings into
   **ship-stoppers** (leaked secrets, exposed/unauthenticated endpoints, injection/RCE,
   TLS off, wildcard CORS, debug on), **review** (lower-impact), and **dark near danger**
   (spots the scanner *couldn't* read that sit next to something dangerous). It's
   PRE-verification — `RED/YELLOW/GREEN` is your starting hypothesis.
5. **Verify every ship-stopper by reading the code.** Open each `where` (file:line),
   confirm it's a real, reachable problem (not a false alarm or test/example code).
   Drop the false ones.
6. **Verify the "dark near danger" spots too.** Open each one and reason about it by
   hand (can untrusted input reach it? does it hit something dangerous?). **This is the
   step that makes your "you're good" trustworthy** — you checked the parts a scanner
   can't see, instead of rubber-stamping.
7. **Give them the verdict** — short, plain, and honest:
   - 🔴 **Not safe to ship yet** — "Fix these N things first:" then a numbered list, each
     one sentence in their terms + "want me to fix it?" Offer to fix.
   - 🟡 **Mostly fine, a couple things to know** — list what to check/fix; say what you
     verified by hand.
   - 🟢 **Safe to ship** — only after you've confirmed no real ship-stoppers AND
     hand-checked the uncertain spots. Say so: *"I checked your endpoints, secrets,
     inputs, and the 4 spots a scanner couldn't read — you're good to deploy."*
8. **Always end with what you couldn't be sure of**, framed as diligence:
   *"One thing I couldn't fully auto-check: X — I read it and it looks fine, but if you
   change it, re-run this."* Never present uncertainty as a scary list of "unknowns."

## Don't
- Don't show raw beacon lists, file dumps, or the JSON — translate to plain risk language.
- Don't say 🟢 without having *read* the ship-stoppers and the dark-near-danger spots.
- Don't edit/"fix" their code without asking.
- Don't run `--deploy` as a one-time gimmick — offer it again each time they ship.

## What the verdict is based on
`--deploy` is recall-biased on the risks that actually sink a freshly-deployed app:
leaked secrets, unauthenticated endpoints, injection / RCE / SSRF / deserialization,
TLS-off, wildcard CORS, debug mode. Detection is the assembled linters + Waypoint's
precise rules; the credibility comes from *you* verifying the flagged items and the
spots the scan couldn't reach. See [the main `waypoint` skill](../waypoint/SKILL.md)
for the full engine and the deeper `--deep` audit.
