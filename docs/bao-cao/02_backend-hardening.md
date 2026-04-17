# Báo cáo: Backend Hardening — Migrations & Integration Tests

## 1. Alembic Migrations

### Vấn đề
Backend dùng `init_db()` với `Base.metadata.create_all` — đơn giản nhưng không theo dõi được lịch sử thay đổi schema, không rollback được.

### Giải pháp
Thêm **Alembic** để quản lý schema migrations có version control.

### Cấu trúc
```
backend/
├── alembic.ini                              Config file
└── alembic/
    ├── env.py                               Async engine setup
    ├── script.py.mako                       Template cho revision files
    └── versions/
        └── 0001_initial_schema.py           Initial schema (4 bảng)
```

### env.py — Async support
Alembic mặc định dùng sync engine. Để hỗ trợ `asyncpg`, `env.py` dùng `async_engine_from_config` và `asyncio.run()`:

```python
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(...)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
```

### Migration 0001 — Initial Schema
4 bảng tạo theo thứ tự đúng (foreign key dependencies):
1. `restaurants` — slug unique, google_place_id unique
2. `reviews` — FK→restaurants, index on restaurant_id
3. `trust_scores` — FK→reviews (1-1 unique)
4. `scrape_jobs` — FK→restaurants (optional)

### Chạy migrations
```bash
cd backend
alembic upgrade head    # apply tất cả migrations
alembic downgrade -1    # rollback 1 bước
alembic current         # xem version hiện tại
alembic history         # xem lịch sử
```

---

## 2. Integration Tests

### Vấn đề
Unit tests (`test_scoring.py`) chỉ test logic thuần — không test API layer (routing, validation, response format).

### Giải pháp
Thêm `tests/test_api.py` dùng **httpx** `AsyncClient` với `ASGITransport` — test trực tiếp ASGI app, không cần server thật và không cần network.

### Test cases (9 tests)

| Test | Mục đích |
|------|---------|
| `test_health` | Endpoint `/health` trả về status ok |
| `test_analyze_short_review` | Review ngắn → trust_score thấp, content_only=True |
| `test_analyze_detailed_review` | Review dài, nhiều aspect → trust_score ≥ 60 |
| `test_analyze_mismatch_review` | Tích cực + sao thấp → sentiment penalty |
| `test_analyze_missing_field` | Thiếu star_rating → 422 |
| `test_analyze_invalid_star` | star_rating=6 → 422 |
| `test_restaurant_not_found` | Slug không tồn tại → 404 |
| `test_scrape_status_not_found` | Job ID không tồn tại → 404 |
| `test_scrape_invalid_url` | URL không phải Google Maps → 422 |

### Validation bổ sung
Thêm `@field_validator("url")` vào `ScrapeRequest`:
```python
if "google.com/maps" not in v and "maps.app.goo.gl" not in v:
    raise ValueError("url phải là link Google Maps")
```

### Chạy tests
```bash
# Tất cả tests
pytest backend/tests/ -v

# Chỉ unit tests (không cần DB/GPU)
pytest backend/tests/test_scoring.py -v

# Chỉ integration tests
pytest backend/tests/test_api.py -v
```

---

## 3. Kết quả

| Hạng mục | Trước | Sau |
|---------|-------|-----|
| Schema migrations | `create_all` (no version) | Alembic versioned |
| API tests | 0 | 9 integration tests |
| URL validation | Không có | Validate Google Maps format |
| Rollback DB | Không thể | `alembic downgrade -1` |
