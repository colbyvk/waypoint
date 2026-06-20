# useEffect async work with no cleanup (React)

- **Axes:** concurrency, edge-case
- **Languages:** TypeScript (React)
- **Generated rule(s):** `waypoint-react-effect-async-no-cleanup`
- **Agent hypothesis:** "async effect without cleanup — unmount/stale-closure race?"

## What it is
A `useEffect` kicks off asynchronous work — a `fetch`, an `await`, a `.then`, or an
`async` body — but does not return a cleanup function. If the component unmounts (or
the inputs change and the effect re-runs) before that async work finishes, the
late-arriving result has nowhere safe to land: it can try to update a component that
is gone, or an older request can overwrite a newer one. The flag marks effects that
start async work without the cleanup that would cancel or ignore a stale result.

## Bad (flagged)
```tsx
// samples/monorepo/react_app/src/UserProfile.tsx
useEffect(() => {
  async function fetchData() {
    const p = await getProfile(userId);
    setBio(p.bioHtml);          // may run after unmount; nothing cancels it
  }
  fetchData();
}, []);                          // no cleanup returned
```

## Acceptable (not a problem)
```tsx
// samples/monorepo/react_app/src/UserProfile.tsx
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/profile/${userId}`, { signal: controller.signal });
  return () => controller.abort();   // cleanup aborts the in-flight request
}, [userId]);
```

## Notes for the agent
- **Confirms a real concern:** the async result is used to set state (or otherwise
  touch the component) AND nothing guards against the component having unmounted or
  the inputs having changed mid-flight.
- **Dismisses it:** the effect returns a cleanup that aborts/ignores the result, an
  `ignore`/`isMounted` flag is checked before setting state, or the async work has
  no effect on the component after it resolves.
- Also glance at the dependency array: `[]` next to a value used inside the effect
  (here `userId`) is a related stale-closure smell.
