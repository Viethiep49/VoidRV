const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function getRestaurant(slug) {
  const res = await fetch(`${BASE}/api/v1/restaurant/${slug}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}
