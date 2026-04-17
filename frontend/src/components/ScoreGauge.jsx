export default function ScoreGauge({ score, label }) {
  const color = score >= 75 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444'
  const pct = Math.round(score)
  const circumference = 2 * Math.PI * 40
  const dashArray = `${(pct / 100) * circumference} ${circumference}`

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-40 h-40">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#1f2937" strokeWidth="10" />
          <circle
            cx="50" cy="50" r="40" fill="none"
            stroke={color} strokeWidth="10"
            strokeDasharray={dashArray}
            strokeLinecap="round"
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold" style={{ color }}>{pct}</span>
          <span className="text-xs text-gray-400">/ 100</span>
        </div>
      </div>
      {label && <span className="text-sm text-gray-400">{label}</span>}
    </div>
  )
}
