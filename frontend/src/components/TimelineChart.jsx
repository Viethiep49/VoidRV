import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  const { count, is_burst } = payload[0].payload
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm">
      <p className="text-gray-400">{label}</p>
      <p className="font-semibold">{count} reviews{is_burst ? ' ⚠ Burst' : ''}</p>
    </div>
  )
}

export default function TimelineChart({ data }) {
  if (!data?.length) return null
  return (
    <div className="rounded-xl border border-gray-800 p-4">
      <h3 className="text-sm font-semibold text-gray-400 mb-4">Reviews theo thời gian</h3>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#6b7280' }} />
          <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[3, 3, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.is_burst ? '#ef4444' : '#3b82f6'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-600 mt-2">Đỏ = ngày bất thường (burst)</p>
    </div>
  )
}
