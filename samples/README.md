# Waypoint sample fixtures — [!] INTENTIONALLY INSECURE

**The code under `samples/` is deliberately vulnerable.** It exists only to
exercise Waypoint's detectors: every file plants known issues — injection,
hardcoded secrets, SSRF, races, logic bugs, IaC misconfig — usually marked with
`WAYPOINT-PLANT` (should fire) and `WAYPOINT-OK` (must stay quiet) comments.

**Do not deploy it, copy it into real projects, or treat its findings as real
vulnerabilities.** It is test data — it is never built or shipped.

- `samples/monorepo/` is a polyglot tree (Python / Rust / TypeScript / React + IaC);
  `samples/monorepo/MANIFEST.md` lists the planted issues.
- GitHub code scanning *will* flag this directory — that's expected. The repo ships
  [`.github/codeql/codeql-config.yml`](../.github/codeql/codeql-config.yml) with a
  `paths-ignore` for `samples/**` so the fixtures don't create noise in the Security
  tab. (Point your CodeQL setup at that config file.)
