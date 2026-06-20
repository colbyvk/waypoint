# infra/experimental/ — retired proxy rules (OFF by default)

These are recall-biased **proxy** detectors: rules that flag a *region that involves*
concurrency / unbounded work / a broad code shape, rather than proving a defect.
Verification on real repos ([../../docs/VALIDATION.md](../../docs/VALIDATION.md))
showed they generate **most of Waypoint's false positives** while finding nothing the
precise rules + off-the-shelf linters don't already catch.

They are **not loaded by the default scan** (`bin/waypoint` reads only `infra/core/`)
and are **not maintained**. They are kept here for reference and opt-in.

**Retired categories** (Python · TypeScript · Rust · React): `concurrency`, `abuse`,
`edge-case`, `authz`.

**What stayed in `infra/core/`** — the genuinely additive rules:
- `security/` — precise injection / crypto / secret / deserialization / SSRF / XSS
  rules, plus the **taint-mode dataflow** rules (source → sink), which a linter does
  not give you for free.
- `logic/` — low-false-positive logic-bug rules (self-comparison, NaN compare, …).
- `iac/` — AWS-CDK misconfig in CDK *source* (which Trivy's IaC scanner doesn't cover).

For the commodity coverage these proxies approximated, use curated **OSS Semgrep
packs** instead (see the README "Detection" section) — e.g.
`SEMGREP_EXTRA="p/owasp-top-ten p/secrets" bin/waypoint <dir>`.

To opt one category back in for a single scan (it is also a valid local Semgrep config):
`SEMGREP_EXTRA="infra/experimental/python/concurrency" bin/waypoint <dir>`.
