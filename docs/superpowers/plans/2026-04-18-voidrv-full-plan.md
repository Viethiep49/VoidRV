# VoidRV — Full Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện hệ thống VoidRV từ backend đã có → frontend hoàn chỉnh → deploy, song song chuẩn bị pipeline ML (train sau khi app xong).

**Architecture:** 2-layer scoring (Content 60% + Behavior 40%), FastAPI async backend đã hoàn thiện, React + Vite frontend cần xây từ scaffold. ML weights chưa có — backend graceful degradation dùng base PhoBERT cho đến khi fine-tune xong.

**Tech Stack:** FastAPI + SQLAlchemy async + PostgreSQL | React 18 + Vite 5 + TailwindCSS 3 + Recharts | PhoBERT (vinai/phobert-base) | Playwright scraper | Alembic migrations | pytest + pytest-asyncio

---

## Trạng thái hiện tại (2026-04-18)

| Phần | Trạng thái |
|------|------------|
| Backend core (services, routers, DB models) | ✅ Xong |
| Unit tests (test_scoring.py) | ✅ Xong |
| Báo cáo backend | ✅ docs/bao-cao/01_backend.md |
| Docs (06 files) | ❌ Lỗi thời (vẫn nói 3-layer) |
| Alembic migrations | ❌ Chưa có |
| Frontend | ❌ Chỉ có src/ scaffold, không có package.json |
| ML weights | ⏸ Defer (train sau) |

---

## Phase 1 — Docs & Plan ✅ (session này)

**Output:** Tất cả docs phản ánh đúng 2-layer thực tế. `docs/plan.md` là master plan.

- [x] Cập nhật `CLAUDE.md` (đã làm)
- [ ] Cập nhật `docs/01_ke-hoach-tong-quan.md` → 2-layer, bỏ Foody (chưa có)
- [ ] Cập nhật `docs/02_kien-truc-he-thong.md` → behavior_module, đúng weights
- [ ] Cập nhật `docs/03_scoring-logic.md` → 60/40, bỏ context layer
- [ ] Cập nhật `docs/04_data-pipeline.md` → hiện trạng, defer note
- [ ] Cập nhật `docs/05_api-specs.md` → endpoint thực tế
- [ ] Viết `docs/plan.md` — master plan ngắn gọn
- [ ] Commit: `docs: sync all docs to 2-layer implementation`

---

## Phase 2 — Backend Hardening

**Output:** DB migrations chạy được, CRUD đầy đủ, test coverage tốt hơn, backend production-ready.

### Task 2.1 — Alembic migrations

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/0001_initial_schema.py`

- [ ] Init alembic trong thư mục backend:
  ```bash
  cd backend
  alembic init alembic
  ```
- [ ] Sửa `alembic/env.py` để import models và dùng async engine:
  ```python
  from backend.db.database import Base
  from backend.db import models  # noqa — import để Alembic thấy models
  target_metadata = Base.metadata
  ```
- [ ] Generate migration đầu tiên:
  ```bash
  alembic revision --autogenerate -m "initial schema"
  ```
- [ ] Review file migration được tạo — kiểm tra 4 bảng: restaurants, reviews, trust_scores, scrape_jobs
- [ ] Test apply:
  ```bash
  alembic upgrade head
  ```
- [ ] Commit: `chore: add alembic migrations`

### Task 2.2 — Integration tests cho API

**Files:**
- Create: `backend/tests/test_api.py`

- [ ] Viết test cho POST /analyze với httpx AsyncClient:
  ```python
  import pytest
  from httpx import AsyncClient, ASGITransport
  from backend.main import app

  @pytest.mark.asyncio
  async def test_analyze_short_review():
      async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
          r = await client.post("/api/v1/analyze", json={"content": "Ngon", "star_rating": 5})
      assert r.status_code == 200
      data = r.json()
      assert "trust_score" in data
      assert data["content_only"] is True
      assert 0 <= data["trust_score"] <= 100

  @pytest.mark.asyncio
  async def test_analyze_good_review():
      async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
          r = await client.post("/api/v1/analyze", json={
              "content": "Phở bò ngon tuyệt, nước dùng đậm đà, giá 50k hợp lý, nhân viên thân thiện, không gian sạch sẽ",
              "star_rating": 5
          })
      assert r.status_code == 200
      assert r.json()["trust_score"] >= 60

  @pytest.mark.asyncio
  async def test_health():
      async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
          r = await client.get("/api/v1/health")
      assert r.status_code == 200
      assert r.json()["status"] == "ok"
  ```
- [ ] Chạy test:
  ```bash
  pytest backend/tests/test_api.py -v
  ```
- [ ] Commit: `test: add API integration tests`

### Task 2.3 — Báo cáo phase 2

- [ ] Viết `docs/bao-cao/02_backend-hardening.md` (migrations + tests)
- [ ] Update `docs/plan.md` — đánh dấu Phase 2 xong

---

## Phase 3 — Frontend Shell (Mock Data)

**Output:** React app chạy được, 3 trang với mock data, UI đúng design spec.

### Task 3.1 — Scaffold Vite + React + TailwindCSS

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/index.css`

- [ ] Tạo package.json:
  ```json
  {
    "name": "voidrv-frontend",
    "version": "1.0.0",
    "type": "module",
    "scripts": {
      "dev": "vite",
      "build": "vite build",
      "preview": "vite preview"
    },
    "dependencies": {
      "react": "^18.3.1",
      "react-dom": "^18.3.1",
      "react-router-dom": "^6.26.2",
      "recharts": "^2.13.0",
      "axios": "^1.7.7"
    },
    "devDependencies": {
      "@vitejs/plugin-react": "^4.3.2",
      "autoprefixer": "^10.4.20",
      "postcss": "^8.4.47",
      "tailwindcss": "^3.4.14",
      "vite": "^5.4.10"
    }
  }
  ```
- [ ] Tạo `vite.config.js`:
  ```js
  import { defineConfig } from 'vite'
  import react from '@vitejs/plugin-react'

  export default defineConfig({
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': 'http://localhost:8000'
      }
    }
  })
  ```
- [ ] Tạo `tailwind.config.js`:
  ```js
  export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    theme: {
      extend: {
        colors: {
          trusted: '#22c55e',
          caution: '#eab308',
          suspicious: '#ef4444',
        }
      }
    },
    plugins: []
  }
  ```
- [ ] Tạo `postcss.config.js`:
  ```js
  export default { plugins: { tailwindcss: {}, autoprefixer: {} } }
  ```
- [ ] Tạo `index.html`:
  ```html
  <!DOCTYPE html>
  <html lang="vi">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>VoidRV — Kiểm tra review nhà hàng</title>
    </head>
    <body>
      <div id="root"></div>
      <script type="module" src="/src/main.jsx"></script>
    </body>
  </html>
  ```
- [ ] Tạo `src/index.css`:
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```
- [ ] Tạo `src/main.jsx`:
  ```jsx
  import React from 'react'
  import ReactDOM from 'react-dom/client'
  import { BrowserRouter } from 'react-router-dom'
  import App from './App'
  import './index.css'

  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  )
  ```
- [ ] Tạo `src/App.jsx`:
  ```jsx
  import { Routes, Route } from 'react-router-dom'
  import HomePage from './pages/HomePage'
  import AnalyzePage from './pages/AnalyzePage'
  import RestaurantPage from './pages/RestaurantPage'

  export default function App() {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/restaurant/:slug" element={<RestaurantPage />} />
        </Routes>
      </div>
    )
  }
  ```
- [ ] `npm install` và chạy thử:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- [ ] Commit: `feat: scaffold frontend with Vite + React + TailwindCSS`

### Task 3.2 — Components: ScoreGauge + Badge

**Files:**
- Create: `frontend/src/components/ScoreGauge.jsx`
- Create: `frontend/src/components/Badge.jsx`

- [ ] Tạo `ScoreGauge.jsx` — hiển thị Trust Score dạng vòng cung:
  ```jsx
  export default function ScoreGauge({ score, label }) {
    const color = score >= 75 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444'
    const pct = Math.round(score)
    return (
      <div className="flex flex-col items-center gap-2">
        <div className="relative w-40 h-40">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#1f2937" strokeWidth="10" />
            <circle
              cx="50" cy="50" r="40" fill="none"
              stroke={color} strokeWidth="10"
              strokeDasharray={`${pct * 2.51} 251`}
              strokeLinecap="round"
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
  ```
- [ ] Tạo `Badge.jsx`:
  ```jsx
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
  ```
- [ ] Commit: `feat: add ScoreGauge and Badge components`

### Task 3.3 — Component: ScoreBreakdown

**Files:**
- Create: `frontend/src/components/ScoreBreakdown.jsx`

- [ ] Tạo `ScoreBreakdown.jsx` — bảng chi tiết signals:
  ```jsx
  export default function ScoreBreakdown({ breakdown, contentOnly }) {
    const rows = [
      { label: 'PhoBERT base',       value: breakdown?.phobert_base,       show: true },
      { label: 'Sentiment check',    value: breakdown?.sentiment_penalty,   show: true },
      { label: 'Aspect bonus',       value: breakdown?.aspect_bonus,        show: true },
      { label: 'TTR',                value: breakdown?.ttr_penalty,         show: true },
      { label: 'Length',             value: breakdown?.length_penalty,      show: true },
      { label: 'Duplicate penalty',  value: breakdown?.duplicate_penalty,   show: true },
      { label: 'Content Score',      value: breakdown?.content_score,       show: true, bold: true },
      { label: 'Behavior Score',     value: breakdown?.behavior_score,      show: !contentOnly, bold: true },
    ]
    return (
      <div className="rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full text-sm">
          <tbody>
            {rows.filter(r => r.show && r.value !== undefined).map(r => (
              <tr key={r.label} className="border-b border-gray-800 last:border-0">
                <td className={`px-4 py-2 text-gray-400 ${r.bold ? 'font-semibold text-gray-200' : ''}`}>{r.label}</td>
                <td className={`px-4 py-2 text-right font-mono ${r.value >= 0 ? 'text-green-400' : 'text-red-400'} ${r.bold ? 'font-semibold' : ''}`}>
                  {r.value >= 0 ? '+' : ''}{Math.round(r.value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }
  ```
- [ ] Commit: `feat: add ScoreBreakdown component`

### Task 3.4 — Trang /analyze (Demo mode)

**Files:**
- Create: `frontend/src/pages/AnalyzePage.jsx`
- Create: `frontend/src/api/analyze.js`

- [ ] Tạo `src/api/analyze.js`:
  ```js
  const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

  export async function analyzeReview(content, starRating) {
    const res = await fetch(`${BASE}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, star_rating: starRating }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }
  ```
- [ ] Tạo `src/pages/AnalyzePage.jsx`:
  ```jsx
  import { useState } from 'react'
  import ScoreGauge from '../components/ScoreGauge'
  import Badge from '../components/Badge'
  import ScoreBreakdown from '../components/ScoreBreakdown'
  import { analyzeReview } from '../api/analyze'

  export default function AnalyzePage() {
    const [text, setText] = useState('')
    const [star, setStar] = useState(5)
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleSubmit(e) {
      e.preventDefault()
      if (!text.trim()) return
      setLoading(true); setError(null)
      try {
        setResult(await analyzeReview(text, star))
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    return (
      <div className="max-w-2xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-6">Phân tích review</h1>
        <form onSubmit={handleSubmit} className="space-y-4 mb-8">
          <textarea
            value={text} onChange={e => setText(e.target.value)}
            placeholder="Dán nội dung review vào đây..."
            rows={5}
            className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-400">Số sao:</label>
            {[1,2,3,4,5].map(n => (
              <button key={n} type="button" onClick={() => setStar(n)}
                className={`w-8 h-8 rounded-full text-sm font-bold ${star === n ? 'bg-yellow-400 text-gray-900' : 'bg-gray-800 text-gray-400'}`}>
                {n}
              </button>
            ))}
          </div>
          <button type="submit" disabled={loading || !text.trim()}
            className="w-full rounded-xl bg-blue-600 py-3 font-semibold hover:bg-blue-500 disabled:opacity-40">
            {loading ? 'Đang phân tích...' : 'Phân tích'}
          </button>
        </form>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {result && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <ScoreGauge score={result.trust_score} label="Trust Score" />
              <div className="text-right space-y-2">
                <Badge badge={result.badge} />
                <p className="text-sm text-gray-400">Void Score: {Math.round(100 - result.trust_score)}</p>
                {result.content_only && (
                  <p className="text-xs text-yellow-500">{result.caveat}</p>
                )}
              </div>
            </div>
            {result.aspects_found?.length > 0 && (
              <div>
                <p className="text-xs text-gray-500 mb-2">Aspects tìm được</p>
                <div className="flex flex-wrap gap-2">
                  {result.aspects_found.map(a => (
                    <span key={a} className="px-2 py-1 text-xs bg-gray-800 rounded-full">{a}</span>
                  ))}
                </div>
              </div>
            )}
            <ScoreBreakdown breakdown={result.breakdown} contentOnly={result.content_only} />
            <div className="space-y-1">
              {result.explanation?.map((line, i) => (
                <p key={i} className="text-sm text-gray-400">{line}</p>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
  ```
- [ ] Test thủ công: chạy `npm run dev`, mở `/analyze`, nhập review
- [ ] Commit: `feat: add /analyze page with real API`

### Task 3.5 — Trang / (HomePage — scrape URL)

**Files:**
- Create: `frontend/src/pages/HomePage.jsx`
- Create: `frontend/src/api/scrape.js`

- [ ] Tạo `src/api/scrape.js`:
  ```js
  const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

  export async function startScrape(url, maxReviews = 50) {
    const res = await fetch(`${BASE}/api/v1/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, max_reviews: maxReviews }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }

  export async function pollScrapeStatus(jobId) {
    const res = await fetch(`${BASE}/api/v1/scrape/status/${jobId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }
  ```
- [ ] Tạo `src/pages/HomePage.jsx`:
  ```jsx
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
        setStatus({ status: 'pending', progress: 0, message: 'Đang khởi động...' })
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
            setError(s.error_message ?? 'Scrape thất bại')
            setJobId(null)
          }
        } catch (err) {
          clearInterval(pollRef.current)
          setError(err.message)
        }
      }, 3000)
      return () => clearInterval(pollRef.current)
    }, [jobId, navigate])

    return (
      <div className="max-w-xl mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl font-bold mb-2">VoidRV</h1>
        <p className="text-gray-400 mb-10">Kiểm tra độ tin cậy review nhà hàng</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            value={url} onChange={e => setUrl(e.target.value)}
            placeholder="Dán link Google Maps nhà hàng..."
            className="w-full rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" disabled={!!jobId || !url.trim()}
            className="w-full rounded-xl bg-blue-600 py-3 font-semibold hover:bg-blue-500 disabled:opacity-40">
            {jobId ? 'Đang phân tích...' : 'Phân tích'}
          </button>
        </form>

        {status && jobId && (
          <div className="mt-8 space-y-2">
            <div className="h-2 w-full rounded-full bg-gray-800">
              <div className="h-2 rounded-full bg-blue-500 transition-all" style={{ width: `${status.progress}%` }} />
            </div>
            <p className="text-sm text-gray-400">{status.message}</p>
          </div>
        )}

        {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}

        <p className="mt-10 text-sm text-gray-600">
          Hoặc <Link to="/analyze" className="text-blue-400 hover:underline">thử demo nhập tay</Link>
        </p>
      </div>
    )
  }
  ```
- [ ] Test thủ công: nhập URL Google Maps → kiểm tra polling bar
- [ ] Commit: `feat: add HomePage with scrape URL + polling`

### Task 3.6 — Trang /restaurant/:slug (Dashboard)

**Files:**
- Create: `frontend/src/pages/RestaurantPage.jsx`
- Create: `frontend/src/components/ReviewList.jsx`
- Create: `frontend/src/components/TimelineChart.jsx`
- Create: `frontend/src/components/RiskReport.jsx`
- Create: `frontend/src/api/restaurant.js`

- [ ] Tạo `src/api/restaurant.js`:
  ```js
  const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

  export async function getRestaurant(slug) {
    const res = await fetch(`${BASE}/api/v1/restaurant/${slug}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res.json()
  }
  ```
- [ ] Tạo `src/components/TimelineChart.jsx`:
  ```jsx
  import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

  export default function TimelineChart({ data }) {
    if (!data?.length) return null
    return (
      <div className="rounded-xl border border-gray-800 p-4">
        <h3 className="text-sm font-semibold text-gray-400 mb-4">Reviews theo thời gian</h3>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={data}>
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#6b7280' }} />
            <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} />
            <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
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
  ```
- [ ] Tạo `src/components/RiskReport.jsx`:
  ```jsx
  const LEVEL_COLOR = { cao: 'text-red-400', trung_binh: 'text-yellow-400', thap: 'text-green-400' }

  export default function RiskReport({ report }) {
    if (!report) return null
    return (
      <div className="rounded-xl border border-gray-800 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Risk Report</h3>
          <span className={`text-sm font-bold ${LEVEL_COLOR[report.risk_level] ?? 'text-gray-400'}`}>
            {report.risk_level?.toUpperCase()}
          </span>
        </div>
        {report.risk_factors?.map((f, i) => (
          <p key={i} className="text-sm text-gray-400">• {f}</p>
        ))}
        <div className="grid grid-cols-3 gap-2 pt-2">
          <Stat label="Suspicious" value={`${Math.round((report.suspicious_ratio ?? 0) * 100)}%`} />
          <Stat label="New accounts" value={`${Math.round((report.new_account_ratio ?? 0) * 100)}%`} />
          <Stat label="Clusters" value={report.cluster_count ?? 0} />
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
  ```
- [ ] Tạo `src/components/ReviewList.jsx`:
  ```jsx
  import Badge from './Badge'
  import ScoreBreakdown from './ScoreBreakdown'
  import { useState } from 'react'

  export default function ReviewList({ reviews }) {
    const [expanded, setExpanded] = useState(null)
    return (
      <div className="space-y-3">
        {reviews?.map(r => (
          <div key={r.id} className="rounded-xl border border-gray-800 p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">{r.reviewer_name ?? 'Ẩn danh'}</span>
                  <span className="text-yellow-400 text-xs">{'★'.repeat(r.star_rating)}</span>
                </div>
                <p className="text-sm text-gray-300 line-clamp-2">{r.content}</p>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                <Badge badge={r.badge} size="sm" />
                <span className="text-xs text-gray-500">Trust: {r.trust_score}</span>
              </div>
            </div>
            <button onClick={() => setExpanded(expanded === r.id ? null : r.id)}
              className="mt-2 text-xs text-blue-400 hover:underline">
              {expanded === r.id ? 'Thu gọn' : 'Chi tiết'}
            </button>
            {expanded === r.id && (
              <div className="mt-3 space-y-2">
                <ScoreBreakdown breakdown={r.breakdown} contentOnly={r.content_only} />
                {r.explanation?.map((line, i) => (
                  <p key={i} className="text-xs text-gray-500">{line}</p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }
  ```
- [ ] Tạo `src/pages/RestaurantPage.jsx`:
  ```jsx
  import { useParams } from 'react-router-dom'
  import { useEffect, useState } from 'react'
  import ScoreGauge from '../components/ScoreGauge'
  import TimelineChart from '../components/TimelineChart'
  import RiskReport from '../components/RiskReport'
  import ReviewList from '../components/ReviewList'
  import { getRestaurant } from '../api/restaurant'

  export default function RestaurantPage() {
    const { slug } = useParams()
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
      getRestaurant(slug).then(setData).catch(err => setError(err.message))
    }, [slug])

    if (error) return <div className="p-10 text-red-400">{error}</div>
    if (!data) return <div className="p-10 text-gray-500">Đang tải...</div>

    const { restaurant, stats, timeline, suspicious_clusters, reviews } = data

    return (
      <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
        <div>
          <h1 className="text-2xl font-bold">{restaurant.name}</h1>
          {restaurant.address && <p className="text-gray-400 text-sm mt-1">{restaurant.address}</p>}
        </div>

        <div className="grid grid-cols-2 gap-6">
          <ScoreGauge score={stats.avg_trust_score ?? 0} label="Trust Score trung bình" />
          <div className="space-y-3">
            <StatBox label="Void Score" value={Math.round(100 - (stats.avg_trust_score ?? 0))} />
            <StatBox label="Adjusted Rating" value={`${(stats.adjusted_rating ?? 0).toFixed(1)} ★`} />
            <StatBox label="Tổng reviews" value={stats.total_reviews} />
            <StatBox label="Review nghi ngờ" value={`${Math.round((stats.suspicious_ratio ?? 0) * 100)}%`} />
          </div>
        </div>

        <TimelineChart data={timeline} />
        <RiskReport report={stats.risk_report} />

        <div>
          <h2 className="text-lg font-semibold mb-4">Tất cả reviews</h2>
          <ReviewList reviews={reviews} />
        </div>
      </div>
    )
  }

  function StatBox({ label, value }) {
    return (
      <div className="rounded-lg border border-gray-800 px-4 py-3">
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-xl font-bold mt-0.5">{value}</p>
      </div>
    )
  }
  ```
- [ ] Test thủ công: sau khi scrape xong, vào `/restaurant/ten-quan`
- [ ] Commit: `feat: add RestaurantPage dashboard with timeline + risk report + review list`

### Task 3.7 — Báo cáo phase 3

- [ ] Viết `docs/bao-cao/03_frontend.md`
- [ ] Update `docs/plan.md` — đánh dấu Phase 3 xong

---

## Phase 4 — ML Pipeline (Defer — train khi sẵn sàng)

**Output:** PhoBERT fine-tuned weights `backend/ml/weights/phobert_voidrv.pt`. Ablation study notebook.

> **Status:** Defer. Backend chạy graceful degradation (base PhoBERT) cho đến khi xong Phase 4.

### Task 4.1 — Dataset preparation
- [ ] Script label data: `data/scripts/label_reviews.py`
- [ ] Merge + clean: `data/scripts/prepare_dataset.py`
- [ ] Target: ~3000–5000 samples (genuine + fake), balanced

### Task 4.2 — Fine-tune PhoBERT
- [ ] Notebook: `notebooks/01_finetune_phobert.ipynb`
- [ ] Target metrics: F1 ≥ 0.83 trên val set
- [ ] Export weights: `backend/ml/weights/phobert_voidrv.pt`

### Task 4.3 — Ablation study
- [ ] Notebook: `notebooks/02_ablation_study.ipynb`
- [ ] So sánh: Content-only vs Content+Behavior

### Task 4.4 — Báo cáo phase 4
- [ ] Viết `docs/bao-cao/04_ml-pipeline.md`
- [ ] Update `docs/plan.md`

---

## Phase 5 — Integration & Deploy

**Output:** App chạy end-to-end, Docker deploy Railway/Render.

### Task 5.1 — End-to-end test
- [ ] Test thủ công 3–5 quán thật: scrape → dashboard
- [ ] Fix bugs phát sinh

### Task 5.2 — Frontend .env
- [ ] Tạo `frontend/.env`:
  ```
  VITE_API_BASE_URL=http://localhost:8000
  ```
- [ ] Tạo `frontend/.env.production`:
  ```
  VITE_API_BASE_URL=https://your-app.railway.app
  ```

### Task 5.3 — Docker Compose kiểm tra
- [ ] `docker-compose up --build` — kiểm tra build thành công
- [ ] Test API + Frontend qua Docker

### Task 5.4 — Deploy Railway
- [ ] Push code → Railway auto-deploy backend
- [ ] Deploy frontend (Vercel hoặc Railway static)

### Task 5.5 — Báo cáo phase 5
- [ ] Viết `docs/bao-cao/05_integration-deploy.md`
- [ ] Update `docs/plan.md` — đánh dấu toàn bộ xong

---

## Checklist báo cáo quá trình

| File | Nội dung |
|------|---------|
| `docs/bao-cao/01_backend.md` | ✅ Kiến trúc, modules, API, tests |
| `docs/bao-cao/02_backend-hardening.md` | Migrations, integration tests |
| `docs/bao-cao/03_frontend.md` | Components, pages, UX flow |
| `docs/bao-cao/04_ml-pipeline.md` | Dataset, fine-tune, ablation, metrics |
| `docs/bao-cao/05_integration-deploy.md` | E2E, Docker, deploy |
