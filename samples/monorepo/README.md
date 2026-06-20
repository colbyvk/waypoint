# Waypoint Sample Monorepo

Intentionally insecure sample monorepo -- Waypoint test fixture. Do not deploy.

This repository is a TEST FIXTURE for the "Waypoint" code-triage scanner. Every
subproject contains deliberately planted code smells and vulnerabilities so that
static scanners can be exercised against known-bad (and a few known-good) patterns.

- This is **intentionally insecure test code**. It is NOT production code.
- Each planted issue has a comment on the line directly above it of the form
  `WAYPOINT-PLANT: <SHAPE_ID> [axes: ...]`.
- Clean / false-positive-control counterparts are marked `WAYPOINT-OK: <description>`.
- See `MANIFEST.md` for the full table of every planted issue.

## Subprojects

| dir | language | build file |
| --- | --- | --- |
| `py_service/` | Python | `requirements.txt` |
| `rust_service/` | Rust (edition 2021) | `Cargo.toml` |
| `react_app/` | React + TypeScript (TSX) | `package.json`, `tsconfig.json` |
| `ts_lib/` | TypeScript | `package.json`, `tsconfig.json` |

Do not deploy any part of this repository.
