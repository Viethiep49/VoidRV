import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { startScrape, pollScrapeStatus } from '../api/scrape'

export default function HomePage() {
  const [url, setUrl] = useState('')
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const pollRef = useRef(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!url.trim()) return
    setError(null)
    try {
      const { job_id } = await startScrape(url)
      setJobId(job_id)
      setStatus({ status: 'pending', progress: 0, message: 'Đang khởi tạo...' })
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    if (!jobId) return
    pollRef.current = setInterval(async () => {
      try {
        const s = await pollScrapeStatus(jobId)
        setStatus(s)
        if (s.status === 'done') {
          clearInterval(pollRef.current)
          navigate(`/restaurant/${s.restaurant_slug}`)
        }
        if (s.status === 'failed') {
          clearInterval(pollRef.current)
          setError(s.message ?? 'Scrape thất bại')
          setJobId(null)
        }
      } catch (err) {
        clearInterval(pollRef.current)
        setError(err.message)
        setJobId(null)
      }
    }, 3000)
    return () => clearInterval(pollRef.current)
  }, [jobId, navigate])

  return (
    <div className="max-w-xl mx-auto px-4 py-20 text-center">
      <div className="mb-10">
        <h1 className="text-5xl font-bold tracking-tight mb-3">VoidRV</h1>
        <p className="text-gray-400">Kiểm tra độ tin cậy review nhà hàng trên Google Maps</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="Dán link Google Maps nhà hàng vào đây..."
          className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={!!jobId || !url.trim()}
          className="w-full rounded-xl bg-blue-600 py-3 font-semibold hover:bg-blue-500 disabled:opacity-40 transition-colors"
        >
          {jobId ? 'Đang phân tích...' : 'Phân tích reviews'}
        </button>
      </form>

      {status && jobId && (
        <div className="mt-8 space-y-2">
          <div className="h-1.5 w-full rounded-full bg-gray-800">
            <div
              className="h-1.5 rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${status.progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-400">{status.message}</p>
          <p className="text-xs text-gray-600">{status.progress}%</p>
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-900 bg-red-950 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <p className="mt-12 text-sm text-gray-600">
        Hoặc{' '}
        <Link to="/analyze" className="text-blue-400 hover:underline">
          thử demo nhập tay
        </Link>{' '}
        để test nhanh 1 review
      </p>
    </div>
  )
}
