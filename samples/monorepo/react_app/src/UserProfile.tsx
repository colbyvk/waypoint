// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
import React, { useState, useEffect } from "react";
import { getProfile } from "./api";

interface Props {
  userId: string;
}

export function UserProfile({ userId }: Props) {
  const [bio, setBio] = useState<string>("");

  useEffect(() => {
    async function fetchData() {
      const p = await getProfile(userId);
      setBio(p.bioHtml);
    }
    // WAYPOINT-PLANT: TS-EFFECT-ASYNC-NOCLEANUP [axes: concurrency,edge-case]
    fetchData();
  }, []);

  // WAYPOINT-OK: effect with cleanup that aborts the in-flight request
  useEffect(() => {
    const controller = new AbortController();
    fetch(`/api/profile/${userId}`, { signal: controller.signal });
    return () => controller.abort();
  }, [userId]);

  return (
    <div>
      {/* WAYPOINT-PLANT: TS-DANGEROUS-HTML [axes: security] */}
      <div dangerouslySetInnerHTML={{ __html: bio }} />
    </div>
  );
}
