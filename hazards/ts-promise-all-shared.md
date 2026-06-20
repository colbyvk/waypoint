# Promise.all/race over operations that may write shared state (TypeScript)

- **Axes:** concurrency
- **Languages:** TypeScript
- **Generated rule(s):** `waypoint-ts-promise-all-race`
- **Agent hypothesis:** "Promise.all/race over concurrent ops — shared-state write race?"

## What it is
`Promise.all`, `Promise.race`, or `Promise.allSettled` runs several operations at the
same time. That is fine when each operation only computes and returns its own value.
It becomes a concern when the operations *write* to something shared — a module-level
array or object, a singleton, a cache — because their writes can interleave in an
order you did not plan, dropping or duplicating data. This is a beacon: it marks the
concurrent region so the agent can check whether anything shared is written inside.

## Bad (flagged)
```ts
// samples/monorepo/ts_lib/src/index.ts
const SEEN: string[] = [];

async function record(tag: string): Promise<void> {
  SEEN.push(tag);                       // writes shared module array
}

export async function recordAll(tags: string[]): Promise<string[]> {
  await Promise.all(tags.map((t) => record(t)));   // concurrent writers to SEEN
  return SEEN;
}
```

## Acceptable (not a problem)
```ts
// No WAYPOINT-OK control exists in the sample; minimal correct version below.
// Each task returns its own value; the array is built once, after all settle.
export async function recordAll(tags: string[]): Promise<string[]> {
  const results = await Promise.all(tags.map((t) => normalize(t)));
  return results;                       // no shared state written mid-flight
}

async function normalize(tag: string): Promise<string> {
  return tag.trim().toLowerCase();      // pure: owns only its return value
}
```

## Notes for the agent
- **Confirms a real concern:** one or more of the concurrent operations mutates
  state that outlives the operation (module global, shared object/array, external
  store) without coordination.
- **Dismisses it:** each operation is pure or only touches its own local data, and
  the combined result is assembled from the returned values after the promises
  settle.
- JavaScript is single-threaded, so the risk here is *interleaving across awaits*
  (lost/duplicated writes, order surprises), not classic CPU-level data races.
