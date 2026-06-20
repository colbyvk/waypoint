// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import React, { useState, useEffect, useCallback } from "react";
import { getStats } from "./api";

interface Props {
  org: string;
}

export function Dashboard({ org }: Props) {
  const [count, setCount] = useState(0);
  const [stats, setStats] = useState<number[]>([]);

  const load = useCallback(async () => {
    const data = await getStats(org);
    // WAYPOINT-PLANT: TS-SETSTATE-IN-ASYNC [axes: concurrency,edge-case]
    setStats(data);
    setCount(data.length);
  }, []);

  // WAYPOINT-PLANT: TS-EXHAUSTIVE-DEPS [axes: concurrency,edge-case]
  useEffect(() => {
    console.log("loading dashboard for", org);
    load();
  }, []);

  return (
    <div>
      <h1>{org}</h1>
      <p>count: {count}</p>
      <p>items: {stats.length}</p>
    </div>
  );
}
