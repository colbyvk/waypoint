# State setter called inside an async callback (React)

- **Axes:** concurrency, edge-case
- **Languages:** TypeScript (React)
- **Generated rule(s):** `waypoint-react-setstate-in-async`
- **Agent hypothesis:** "setState inside async callback — stale-closure / out-of-order update race?"

## What it is
A React state setter (a function named `set...`) is called *after* an `await` inside
an async function or arrow callback. Two things can go wrong. First, the values the
callback captured may be stale by the time it resumes — the component may have
re-rendered with newer props/state in between. Second, if the callback can run more
than once, a slow earlier call can finish *after* a faster later one and clobber the
fresher result. The flag marks setters reached from inside async callbacks so the
agent can judge whether either race actually bites here.

## Bad (flagged)
```tsx
// samples/monorepo/react_app/src/Dashboard.tsx
const load = useCallback(async () => {
  const data = await getStats(org);
  setStats(data);          // runs after await — captured values may be stale,
  setCount(data.length);   // and a later call could finish first
}, []);
```

## Acceptable (not a problem)
```tsx
// No WAYPOINT-OK control exists in the sample; minimal correct version below.
// Ignore the result if a newer run has started or the component unmounted.
const load = useCallback(async () => {
  let active = true;
  const data = await getStats(org);
  if (active) setStats(data);   // guarded: stale runs are dropped
  return () => { active = false; };
}, [org]);
```

## Notes for the agent
- **Confirms a real concern:** the callback can fire repeatedly (event handler,
  effect that re-runs) AND it reads captured props/state that change AND there is no
  guard dropping stale results.
- **Dismisses it:** the setter uses the functional updater form
  (`setX(prev => ...)`) so it never reads stale captured state, the callback runs
  exactly once, or a "still the latest / still mounted" guard is present.
- The dependency list matters: `[]` on a callback that uses `org` is part of the
  same staleness smell.
