const ROWS = [
  { key: 'phobert_base',       label: 'PhoBERT base' },
  { key: 'sentiment_penalty',  label: 'Sentiment check' },
  { key: 'aspect_bonus',       label: 'Aspect bonus' },
  { key: 'ttr_penalty',        label: 'TTR' },
  { key: 'length_penalty',     label: 'Length' },
  { key: 'duplicate_penalty',  label: 'Duplicate' },
  { key: 'content_score',      label: 'Content Score', bold: true },
  { key: 'behavior_score',     label: 'Behavior Score', bold: true, behaviorOnly: true },
]

export default function ScoreBreakdown({ breakdown, contentOnly }) {
  if (!breakdown) return null
  const rows = ROWS.filter(r => {
    if (r.behaviorOnly && contentOnly) return false
    return breakdown[r.key] !== undefined && breakdown[r.key] !== null
  })

  return (
    <div className="rounded-xl border border-gray-800 overflow-hidden">
      <p className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-800">
        Score Breakdown
      </p>
      <table className="w-full text-sm">
        <tbody>
          {rows.map(r => (
            <tr key={r.key} className="border-b border-gray-800 last:border-0">
              <td className={`px-4 py-2 ${r.bold ? 'font-semibold text-gray-200' : 'text-gray-400'}`}>
                {r.label}
              </td>
              <td className={`px-4 py-2 text-right font-mono ${
                r.bold ? 'font-semibold text-gray-200' :
                breakdown[r.key] >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {!r.bold && breakdown[r.key] >= 0 ? '+' : ''}{Math.round(breakdown[r.key])}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
