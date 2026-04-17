# Báo cáo: Frontend — React + Vite + TailwindCSS

## 1. Tech Stack

| Thư viện | Phiên bản | Vai trò |
|---------|-----------|---------|
| React | 18.3.1 | UI framework |
| Vite | 5.4.10 | Build tool + dev server |
| TailwindCSS | 3.4.14 | Utility CSS |
| react-router-dom | 6.x | Client-side routing |
| Recharts | 2.x | Timeline BarChart |

---

## 2. Cấu trúc

```
frontend/
├── index.html
├── vite.config.js        Dev proxy /api → localhost:8000
├── tailwind.config.js    Custom colors: trusted/caution/suspicious
├── src/
│   ├── main.jsx          Entry: BrowserRouter + App
│   ├── App.jsx           Routes: / · /analyze · /restaurant/:slug
│   ├── api/
│   │   ├── analyze.js    POST /api/v1/analyze
│   │   ├── scrape.js     POST /api/v1/scrape + GET /status/{id}
│   │   └── restaurant.js GET /api/v1/restaurant/{slug}
│   ├── components/
│   │   ├── ScoreGauge.jsx      SVG gauge (0–100, màu theo badge)
│   │   ├── Badge.jsx           trusted/caution/suspicious pill
│   │   ├── ScoreBreakdown.jsx  Bảng signals chi tiết
│   │   ├── TimelineChart.jsx   Recharts BarChart, burst day đỏ
│   │   ├── RiskReport.jsx      risk_level + factors + stats
│   │   └── ReviewList.jsx      Expandable review cards
│   └── pages/
│       ├── HomePage.jsx        URL input + polling bar + redirect
│       ├── AnalyzePage.jsx     Demo: text input + sao + result
│       └── RestaurantPage.jsx  Dashboard đầy đủ
```

---

## 3. Design decisions

### Dark theme (bg-gray-950)
Màu nền tối, badge dùng màu semantic: xanh/vàng/đỏ phản ánh mức độ trust. Nhất quán với branding "Void" (khoảng tối, ẩn sau review).

### Dev proxy
Vite proxy `/api` → `localhost:8000` — tránh CORS trong dev. Production dùng `VITE_API_BASE_URL`.

### Polling pattern (HomePage)
```
startScrape(url) → jobId
setInterval(3s):
    pollScrapeStatus(jobId)
    status=done → navigate(/restaurant/slug)
    status=failed → show error, clear interval
```
Cleanup interval khi component unmount (useRef + useEffect return).

### Expandable reviews (ReviewList)
Mặc định collapse — tránh overload UI. Click "Chi tiết signals" mở ScoreBreakdown + explanation + aspects.

---

## 4. Components

### ScoreGauge
SVG circle với `strokeDasharray` tính từ score. Animate bằng CSS transition. Màu thay đổi theo ngưỡng 75/50.

### ScoreBreakdown
Filter các row theo key có trong `breakdown` và `contentOnly` flag. Hiển thị `+` trước số dương, màu xanh/đỏ.

### TimelineChart
Recharts `BarChart` với custom `Cell` — `is_burst=true` → màu đỏ (`#ef4444`), bình thường → xanh (`#3b82f6`).

### RiskReport
Border màu theo `risk_level`. Stats grid: suspicious%, new_account%, cluster count.

---

## 5. Chạy frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

Frontend dev server proxy `/api/*` → backend `localhost:8000`. Cần backend đang chạy.
