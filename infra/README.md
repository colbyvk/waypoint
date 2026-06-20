# infra/ — Waypoint's detection infrastructure

Two halves, kept side by side:

| Folder | What it is | Tracked in git? |
|---|---|---|
| [`core/`](core/README.md) | The **rules** — Waypoint's custom Semgrep patterns (language-first, then classifier) plus the isolated ESLint/mypy/ruff configs the static tiers run. This is the genuinely custom surface. | yes |
| [`schema-infra/`](schema-infra/README.md) | The **beacon schema** — one generated `.md` per beacon (what it is, where the detection code lives, which linter raises it). Derived from `core/` by `detectors/gen_schema_infra.py`. | only the README; the per-beacon docs are generated on demand |

The plain-English source of truth the rules are written from lives one level up in
[`../hazards/`](../hazards/).
