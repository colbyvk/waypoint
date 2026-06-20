// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.

interface Config {
  name?: string;
  port?: number;
}

export function computeName(cfg: Config): string {
  // WAYPOINT-PLANT: TS-NONNULL-DEREF [axes: edge-case]
  return cfg.name!.toUpperCase();
}

const SEEN: string[] = [];

async function record(tag: string): Promise<void> {
  // WAYPOINT-PLANT: TS-PROMISE-ALL-SHARED [axes: concurrency]
  SEEN.push(tag);
}

export async function recordAll(tags: string[]): Promise<string[]> {
  await Promise.all(tags.map((t) => record(t)));
  return SEEN;
}

// WAYPOINT-OK: guards undefined before use instead of non-null assertion
export function computeNameSafe(cfg: Config): string {
  if (!cfg.name) return "anonymous";
  return cfg.name.toUpperCase();
}
