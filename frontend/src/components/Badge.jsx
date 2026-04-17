const CONFIG = {
  trusted:    { label: 'Đáng tin cậy',   bg: 'bg-green-900',  text: 'text-green-400',  border: 'border-green-700' },
  caution:    { label: 'Cần thận trọng', bg: 'bg-yellow-900', text: 'text-yellow-400', border: 'border-yellow-700' },
  suspicious: { label: 'Nghi ngờ',       bg: 'bg-red-900',    text: 'text-red-400',    border: 'border-red-700' },
}

export default function Badge({ badge, size = 'md' }) {
  const c = CONFIG[badge] ?? CONFIG.caution
  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'
  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${px} ${c.bg} ${c.text} ${c.border}`}>
      {c.label}
    </span>
  )
}
