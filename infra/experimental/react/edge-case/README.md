# react / edge-case

No custom Semgrep rule lives here — React's highest-value edge-case signal is
the **incomplete `useEffect` dependency array**, which is covered off-the-shelf
by `eslint-plugin-react-hooks` (`react-hooks/exhaustive-deps`). That tool's
output is ingested as beacons and tagged `concurrency, edge-case` via the `eslint`
block in `../../../tag_map.yaml`.

The async-effect / stale-setState edge-case shapes are flagged by the rules in
`../concurrency/react.yaml` (they carry the `edge-case` axis alongside
`concurrency`). Add a rule here only if you find a React-specific edge-case shape
that ESLint misses.
