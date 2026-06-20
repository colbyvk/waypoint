# Security Policy

## Reporting a vulnerability

Please report security issues **privately — do not open a public issue or PR**.

- **Preferred:** GitHub private vulnerability reporting — the repo's **Security** tab → **Report a vulnerability**. (Maintainers: enable it under Settings → Code security.)
- If that is unavailable, contact the maintainers through the private channel listed on the repository.

We aim to **acknowledge within 3 business days** and to share a fix or mitigation timeline within **14 days**. Please allow a reasonable window to remediate before public disclosure; we're glad to credit reporters.

## Supported versions

Waypoint is pre-1.0. Security fixes land on `main` (latest). Pin a commit or tag if you need stability.

## Threat model — what executes code, and when

Waypoint scans potentially **untrusted** code, so the dominant risk is *"scanning a hostile repository compromises the host."* Know which tiers run the scanned code:

| Tier | Runs the scanned code? | Safe on untrusted code? |
|---|---|---|
| **fast** (default) / `--changed` | No — static analysis only | [x] Yes |
| `--codeql` | No — builds a database (Python/JS extraction) | [x] Yes |
| `--logic` / `--deep` | **Yes** — runs the target's tests, fuzzers, build scripts | [!] **No** — gated; use the sandbox |

## Hardening in place

- **Static tiers never execute target config.** Waypoint runs its OWN ESLint/mypy config (`--no-config-lookup`, `--config-file=…`), never the scanned project's — a project's `eslint.config.js`/`mypy.ini` can import (execute) plugins.
- **Dynamic tiers are gated.** `--logic`/`--deep` refuse to run unless you pass `--i-trust-this-code` (or set `WAYPOINT_TRUSTED=1`).
- **Sandbox for untrusted code.** `bin/waypoint-sandboxed <dir> --deep` runs in a container with **no network, read-only source mount, non-root, all capabilities dropped, ephemeral filesystem**.
- **Verified downloads.** `detectors/install_codeql.sh` verifies the CodeQL bundle's SHA-256 (fail-closed; pinned version + `gh attestation` fallback).
- **Read-only on your source.** Output goes to `beacons/` and `reports/` (git-ignored). **Detected secrets are redacted** from beacons; raw `reports/` may still contain sensitive matches — do not commit or share it.
- **Path containment.** Waypoint only reads files inside the scanned tree (no `..`/symlink escape).
- **No shell injection in the agent dispatch** (commands are argv lists, not shell strings); all YAML is parsed with `yaml.safe_load`.

## Scope

In scope: anything that lets *scanning a repository* compromise the host, exfiltrate data, escape the scanned tree, or subvert the install/verification path.

Out of scope: findings about the **intentionally vulnerable fixtures** under `samples/` — they exist to exercise the detectors and are not shipped/deployed.
