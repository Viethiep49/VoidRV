const LEVEL = {
  cao:        { label: 'Cao',         color: 'text-red-400',    border: 'border-red-900' },
  trung_binh: { label: 'Trung bình', color: 'text-yellow-400', border: 'border-yellow-900' },
  thap:       { label: 'Thấp',        color: 'text-green-400',  border: 'border-green-900' },
}

export default function RiskReport({ report }) {
  if (!report) return null
  const level = LEVEL[report.risk_level] ?? LEVEL.trung_binh

  return (
    <div className={`rounded-xl border p-4 space-y-3 ${level.border}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Risk Report</h3>
        <span className={`text-sm font-bold ${level.color}`}>
          Rủi ro {level.label}
        </span>
      </div>

      {report.risk_factors?.map((f, i) => (
        <p key={i} className="text-sm text-gray-400">• {f}</p>
      ))}

      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-gray-800">
        <Stat label="Nghi ngờ" value={`${Math.round((report.suspicious_ratio ?? 0) * 100)}%`} />
        <Stat label="Tài khoản mới" value={`${Math.round((report.new_account_ratio ?? 0) * 100)}%`} />
        <Stat label="Clusters" value={report.suspicious_clusters ?? 0} />
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="text-center">
      <p className="text-lg font-bold">{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  )
}
