const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function analyzeReview(content, starRating) {
  const res = await fetch(`${BASE}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, star_rating: starRating }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail?.[0]?.msg ?? `HTTP ${res.status}`)
  }
  return res.json()
}
