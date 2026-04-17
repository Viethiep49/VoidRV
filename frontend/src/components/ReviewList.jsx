import { useState } from 'react'
import Badge from './Badge'
import ScoreBreakdown from './ScoreBreakdown'

export default function ReviewList({ reviews }) {
  const [expanded, setExpanded] = useState(null)

  if (!reviews?.length) return <p className="text-gray-500 text-sm">Không có reviews.</p>

  return (
    <div className="space-y-3">
      {reviews.map(r => (
        <div key={r.id} className="rounded-xl border border-gray-800 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="text-sm font-medium">{r.reviewer_name ?? 'Ẩn danh'}</span>
                {r.reviewer_review_count != null && (
                  <span className="text-xs text-gray-500">{r.reviewer_review_count} bài đánh giá</span>
                )}
                <span className="text-yellow-400 text-xs">{'★'.repeat(r.star_rating)}</span>
              </div>
              <p className="text-sm text-gray-300 line-clamp-2">{r.content}</p>
            </div>
            <div className="flex flex-col items-end gap-1.5 shrink-0">
              <Badge badge={r.badge} size="sm" />
              <span className="text-xs text-gray-500">Trust: {r.trust_score}</span>
            </div>
          </div>

          <button
            onClick={() => setExpanded(expanded === r.id ? null : r.id)}
            className="mt-2 text-xs text-blue-400 hover:underline"
          >
            {expanded === r.id ? 'Thu gọn' : 'Chi tiết signals'}
          </button>

          {expanded === r.id && (
            <div className="mt-3 space-y-3">
              {r.content_only && (
                <p className="text-xs text-yellow-500">Chỉ có Content Score (demo mode)</p>
              )}
              <ScoreBreakdown breakdown={r.breakdown} contentOnly={r.content_only} />
              <div className="space-y-1">
                {r.explanation?.map((line, i) => (
                  <p key={i} className="text-xs text-gray-500">{line}</p>
                ))}
              </div>
              {r.aspects_found?.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {r.aspects_found.map(a => (
                    <span key={a} className="px-2 py-0.5 text-xs bg-gray-800 rounded-full text-gray-400">{a}</span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
