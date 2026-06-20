// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.

export function isAllWords(input: string): boolean {
  // WAYPOINT-PLANT: TS-REDOS [axes: abuse,security]
  const re = /(\w+)+$/;
  return re.test(input);
}

// WAYPOINT-OK: JSON.parse wrapped in try/catch with a safe fallback
export function safeParse<T>(raw: string, fallback: T): T {
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}
