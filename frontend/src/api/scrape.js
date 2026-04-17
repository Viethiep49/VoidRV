const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function startScrape(url, maxReviews = 50) {
  const res = await fetch(`${BASE}/api/v1/scrape`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, max_reviews: maxReviews }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail?.[0]?.msg ?? err?.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function pollScrapeStatus(jobId) {
  const res = await fetch(`${BASE}/api/v1/scrape/status/${jobId}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
