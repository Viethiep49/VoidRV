import { useParams, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import ScoreGauge from '../components/ScoreGauge'
import TimelineChart from '../components/TimelineChart'
import RiskReport from '../components/RiskReport'
import ReviewList from '../components/ReviewList'
import Badge from '../components/Badge'
import { getRestaurant } from '../api/restaurant'

export default function RestaurantPage() {
  const { slug } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getRestaurant(slug).then(setData).catch(err => setError(err.message))
  }, [slug])

  if (error) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <p className="text-red-400 mb-4">{error}</p>
        <Link to="/" className="text-sm text-blue-400 hover:underline">← Về trang chủ</Link>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <div className="inline-block w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-gray-500 text-sm">Đang tải...</p>
      </div>
    )
  }

  const { restaurant, stats, risk_report, timeline, suspicious_clusters, reviews } = data

  const badgeDistrib = stats.distribution ?? {}
  const trustedPct = Math.round(badgeDistrib.trusted ?? 0)
  const cautionPct = Math.round(badgeDistrib.caution ?? 0)
  const suspiciousPct = Math.round(badgeDistrib.suspicious ?? 0)

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{restaurant.name}</h1>
          {restaurant.address && (
            <p className="text-gray-400 text-sm mt-1">{restaurant.address}</p>
          )}
          {restaurant.last_scraped_at && (
            <p className="text-gray-600 text-xs mt-1">
              Cập nhật: {new Date(restaurant.last_scraped_at).toLocaleDateString('vi-VN')}
            </p>
          )}
        </div>
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-300 shrink-0">← Về trang chủ</Link>
      </div>

      {/* Score overview */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border border-gray-800 p-6 flex flex-col items-center">
          <ScoreGauge score={stats.avg_trust_score ?? 0} label="Trust Score trung bình" />
        </div>
        <div className="rounded-xl border border-gray-800 p-4 space-y-3">
          <StatBox label="Void Score" value={Math.round(100 - (stats.avg_trust_score ?? 0))} />
          <StatBox
            label="Adjusted Rating"
            value={`${(stats.avg_star_rating ?? 0).toFixed(1)} ★`}
          />
          <StatBox label="Tổng reviews" value={stats.total_reviews ?? 0} />
        </div>
      </div>

      {/* Badge distribution */}
      <div className="rounded-xl border border-gray-800 p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Phân loại reviews</p>
        <div className="flex gap-3 flex-wrap">
          <BadgeStat badge="trusted" pct={trustedPct} />
          <BadgeStat badge="caution" pct={cautionPct} />
          <BadgeStat badge="suspicious" pct={suspiciousPct} />
        </div>
        <div className="mt-3 h-2 rounded-full overflow-hidden flex">
          <div className="bg-green-500 transition-all" style={{ width: `${trustedPct}%` }} />
          <div className="bg-yellow-500 transition-all" style={{ width: `${cautionPct}%` }} />
          <div className="bg-red-500 transition-all" style={{ width: `${suspiciousPct}%` }} />
        </div>
      </div>

      <TimelineChart data={timeline} />
      <RiskReport report={risk_report} />

      {suspicious_clusters?.length > 0 && (
        <div className="rounded-xl border border-gray-800 p-4">
          <h3 className="text-sm font-semibold mb-3">Suspicious Clusters ({suspicious_clusters.length})</h3>
          <div className="space-y-2">
            {suspicious_clusters.map(c => (
              <div key={c.cluster_id} className="flex items-center justify-between text-sm">
                <span className="text-gray-400">
                  {c.review_ids.length} reviews giống nhau · similarity {Math.round(c.similarity * 100)}%
                </span>
                <span className="text-gray-600 text-xs">{c.review_ids.join(', ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-4">Tất cả reviews ({reviews?.length ?? 0})</h2>
        <ReviewList reviews={reviews} />
      </div>
    </div>
  )
}

function StatBox({ label, value }) {
  return (
    <div className="rounded-lg border border-gray-800 px-3 py-2.5">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-xl font-bold mt-0.5">{value}</p>
    </div>
  )
}

function BadgeStat({ badge, pct }) {
  return (
    <div className="flex items-center gap-2">
      <Badge badge={badge} size="sm" />
      <span className="text-sm font-semibold">{pct}%</span>
    </div>
  )
}
