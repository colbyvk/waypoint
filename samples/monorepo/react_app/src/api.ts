// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.

export async function getProfile(userId: string): Promise<{ bioHtml: string }> {
  const res = await fetch(`/api/profile/${userId}`);
  return res.json();
}

export async function getStats(org: string): Promise<number[]> {
  const res = await fetch(`/api/stats/${org}`);
  return res.json();
}
