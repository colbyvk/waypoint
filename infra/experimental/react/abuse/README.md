# react / abuse

No React-specific abuse rule lives here — the abuse shapes that show up in
React code (ReDoS, input-amplification) are language-general JavaScript/TypeScript
concerns, so they are authored once in `../../typescript/abuse/` and apply to
`.tsx` too (Semgrep's `typescript` language parses JSX).

Add a rule here only for an abuse shape that is genuinely React-specific.
