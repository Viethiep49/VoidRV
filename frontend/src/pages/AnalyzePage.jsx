import { useState } from 'react'
import { Link } from 'react-router-dom'
import ScoreGauge from '../components/ScoreGauge'
import Badge from '../components/Badge'
import ScoreBreakdown from '../components/ScoreBreakdown'
import { analyzeReview } from '../api/analyze'

const STAR_LABELS = { 1: 'Rất tệ', 2: 'Tệ', 3: 'Bình thường', 4: 'Tốt', 5: 'Xuất sắc' }

export default function AnalyzePage() {
  const [text, setText] = useState('')
  const [star, setStar] = useState(5)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await analyzeReview(text.trim(), star))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Phân tích review</h1>
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-300">← Trang chủ</Link>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Dán nội dung review vào đây..."
          rows={5}
          className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-sm placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />

        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400 shrink-0">Số sao:</span>
          <div className="flex gap-1.5">
            {[1, 2, 3, 4, 5].map(n => (
              <button
                key={n}
                type="button"
                onClick={() => setStar(n)}
                title={STAR_LABELS[n]}
                className={`w-9 h-9 rounded-full text-sm font-bold transition-colors ${
                  star === n ? 'bg-yellow-400 text-gray-900' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
          <span className="text-sm text-gray-500">{STAR_LABELS[star]}</span>
        </div>

        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="w-full rounded-xl bg-blue-600 py-3 font-semibold hover:bg-blue-500 disabled:opacity-40 transition-colors"
        >
          {loading ? 'Đang phân tích...' : 'Phân tích'}
        </button>
      </form>

      {error && (
        <div className="rounded-lg border border-red-900 bg-red-950 px-4 py-3 text-sm text-red-400 mb-4">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-800 p-6 flex items-center justify-between gap-6">
            <ScoreGauge score={result.trust_score} label="Trust Score" />
            <div className="space-y-3">
              <Badge badge={result.badge} />
              <div className="space-y-1">
                <p className="text-sm text-gray-400">
                  Void Score: <span className="font-semibold text-gray-200">{Math.round(100 - result.trust_score)}</span>
                </p>
                <p className="text-sm text-gray-400">
                  Confidence: <span className="font-semibold text-gray-200">{Math.round((result.confidence ?? 0) * 100)}%</span>
                </p>
              </div>
              {result.content_only && (
                <p className="text-xs text-yellow-500 max-w-48">{result.caveat}</p>
              )}
            </div>
          </div>

          {result.aspects_found?.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2 uppercase tracking-wide">Aspects</p>
              <div className="flex flex-wrap gap-2">
                {result.aspects_found.map(a => (
                  <span key={a} className="px-2.5 py-1 text-xs bg-gray-800 rounded-full text-gray-300">{a}</span>
                ))}
              </div>
            </div>
          )}

          <ScoreBreakdown breakdown={result.breakdown} contentOnly={result.content_only} />

          <div className="space-y-1.5">
            {result.explanation?.map((line, i) => (
              <p key={i} className="text-sm text-gray-400">{line}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
