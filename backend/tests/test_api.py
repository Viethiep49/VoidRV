"""
Integration tests cho API endpoints.
Dùng httpx AsyncClient + ASGITransport — không cần server thật.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "model_loaded" in body


@pytest.mark.asyncio
async def test_analyze_short_review():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/analyze", json={"content": "Ngon", "star_rating": 5})
    assert r.status_code == 200
    data = r.json()
    assert "trust_score" in data
    assert data["content_only"] is True
    assert 0 <= data["trust_score"] <= 100
    assert data["badge"] in ("trusted", "caution", "suspicious")


@pytest.mark.asyncio
async def test_analyze_detailed_review():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/analyze", json={
            "content": (
                "Phở bò ngon tuyệt, nước dùng đậm đà thơm lừng. "
                "Nhân viên phục vụ nhanh và thân thiện. "
                "Giá 65k một tô, khá hợp lý. Không gian sạch sẽ, thoáng mát."
            ),
            "star_rating": 5,
        })
    assert r.status_code == 200
    data = r.json()
    assert data["trust_score"] >= 60
    assert len(data.get("aspects_found", [])) >= 2
    assert data["content_only"] is True


@pytest.mark.asyncio
async def test_analyze_mismatch_review():
    """Nội dung tích cực nhưng sao thấp → sentiment penalty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/analyze", json={
            "content": "Quán ngon tuyệt vời, thích lắm, hài lòng, sẽ quay lại",
            "star_rating": 1,
        })
    assert r.status_code == 200
    data = r.json()
    # Sentiment mismatch → lower score
    assert data["trust_score"] < 80


@pytest.mark.asyncio
async def test_analyze_missing_field():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/analyze", json={"content": "Ngon"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_analyze_invalid_star():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/analyze", json={"content": "Ngon", "star_rating": 6})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_restaurant_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/restaurant/quan-khong-ton-tai-xyz123")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_scrape_status_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/scrape/status/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_scrape_invalid_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/v1/scrape", json={"url": "not-a-valid-google-maps-url"})
    assert r.status_code == 422
