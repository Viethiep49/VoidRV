"""
Google Maps scraper dùng Playwright.
Scrape review cards: text, star, reviewer_name, reviewer_review_count, timestamp.
"""

from __future__ import annotations
import asyncio
import logging
import random
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)

# Selectors — có thể thay đổi khi Google update UI
REVIEWS_BUTTON_SELECTOR = 'button[aria-label*="đánh giá"], button[aria-label*="Reviews"], button[data-tab-index="1"]'
REVIEW_CARD_SELECTOR = '[data-review-id]'
REVIEW_TEXT_SELECTOR = 'span[data-expandable-section], .MyEned span'
STAR_SELECTOR = 'span[aria-label*="sao"], span[aria-label*="star"]'
REVIEWER_NAME_SELECTOR = '.d4r55'
REVIEWER_COUNT_SELECTOR = '.RfnDt span'
DATE_SELECTOR = '.rsqaWe'
RESTAURANT_NAME_SELECTOR = 'h1.DUwDvf'
RESTAURANT_ADDRESS_SELECTOR = 'button[data-item-id="address"] .Io6YTe'


@dataclass
class ScrapedReview:
    content: str
    star_rating: int
    reviewer_name: str | None = None
    reviewer_review_count: int | None = None
    posted_relative: str | None = None  # "3 tuần trước"
    posted_at: datetime | None = None   # computed


@dataclass
class ScrapedRestaurant:
    name: str
    address: str | None = None
    google_place_id: str | None = None
    google_maps_url: str = ""
    reviews: list[ScrapedReview] = field(default_factory=list)


def parse_place_id_from_url(url: str) -> str | None:
    """Trích xuất place_id hoặc CID từ Google Maps URL."""
    patterns = [
        r"place/[^/]+/([^/?]+)",          # /place/Name/ChIJ...
        r"!1s(ChIJ[^!]+)",                 # !1sChIJ...
        r"cid=(\d+)",                      # ?cid=12345
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def _parse_relative_date(text: str) -> datetime | None:
    """
    Convert "3 tuần trước", "2 tháng trước", "1 năm trước" → datetime.
    Mất precision nhưng đủ cho behavior scoring.
    """
    now = datetime.utcnow()
    text = text.strip().lower()

    patterns = [
        (r"(\d+)\s*(giây|giây trước)", lambda n: now - timedelta(seconds=int(n))),
        (r"(\d+)\s*(phút|phút trước)", lambda n: now - timedelta(minutes=int(n))),
        (r"(\d+)\s*(giờ|giờ trước)", lambda n: now - timedelta(hours=int(n))),
        (r"(\d+)\s*(ngày|ngày trước)", lambda n: now - timedelta(days=int(n))),
        (r"(\d+)\s*(tuần|tuần trước)", lambda n: now - timedelta(weeks=int(n))),
        (r"(\d+)\s*(tháng|tháng trước)", lambda n: now - timedelta(days=int(n) * 30)),
        (r"(\d+)\s*(năm|năm trước)", lambda n: now - timedelta(days=int(n) * 365)),
        # English fallback
        (r"(\d+)\s*second", lambda n: now - timedelta(seconds=int(n))),
        (r"(\d+)\s*minute", lambda n: now - timedelta(minutes=int(n))),
        (r"(\d+)\s*hour", lambda n: now - timedelta(hours=int(n))),
        (r"(\d+)\s*day", lambda n: now - timedelta(days=int(n))),
        (r"(\d+)\s*week", lambda n: now - timedelta(weeks=int(n))),
        (r"(\d+)\s*month", lambda n: now - timedelta(days=int(n) * 30)),
        (r"(\d+)\s*year", lambda n: now - timedelta(days=int(n) * 365)),
        (r"a month", lambda n: now - timedelta(days=30)),
        (r"a year", lambda n: now - timedelta(days=365)),
        (r"a week", lambda n: now - timedelta(weeks=1)),
    ]

    for pattern, fn in patterns:
        m = re.search(pattern, text)
        if m:
            try:
                groups = m.groups()
                return fn(groups[0] if groups else 1)
            except Exception:
                pass
    return None


def _parse_review_count(text: str) -> int | None:
    """
    Parse "47 bài đánh giá" → 47.
    Parse "47 reviews" → 47.
    """
    m = re.search(r"(\d+)", text.replace(".", "").replace(",", ""))
    return int(m.group(1)) if m else None


def _parse_star_rating(aria_label: str) -> int:
    """Parse "5 sao" or "5 stars" → 5."""
    m = re.search(r"(\d)", aria_label)
    return int(m.group(1)) if m else 0


async def _random_delay(min_ms: int = 500, max_ms: int = 1500):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


async def _scroll_reviews_panel(page: Page, max_scrolls: int = 30):
    """Scroll panel reviews để load thêm (lazy load)."""
    try:
        panel = await page.query_selector('[role="feed"]')
        if not panel:
            panel = await page.query_selector('.m6QErb')
        if not panel:
            return

        prev_count = 0
        for _ in range(max_scrolls):
            await panel.evaluate("el => el.scrollBy(0, 1000)")
            await _random_delay(800, 1500)
            cards = await page.query_selector_all(REVIEW_CARD_SELECTOR)
            if len(cards) == prev_count:
                break  # Không load thêm
            prev_count = len(cards)
    except Exception as e:
        logger.warning(f"Scroll error: {e}")


async def _extract_review_card(card) -> ScrapedReview | None:
    """Extract data từ 1 review card element."""
    try:
        # Text content
        text_el = await card.query_selector(REVIEW_TEXT_SELECTOR)
        if not text_el:
            # Fallback: lấy all text
            content = (await card.inner_text()).strip()
        else:
            # Click "Xem thêm" nếu có
            more_btn = await card.query_selector('button[aria-expanded="false"]')
            if more_btn:
                await more_btn.click()
                await _random_delay(200, 400)
            content = (await text_el.inner_text()).strip()

        if not content or len(content) < 2:
            return None

        # Star rating
        star_el = await card.query_selector(STAR_SELECTOR)
        star_rating = 0
        if star_el:
            label = await star_el.get_attribute("aria-label") or ""
            star_rating = _parse_star_rating(label)
        if star_rating == 0:
            return None  # Skip review không có sao

        # Reviewer name
        name_el = await card.query_selector(REVIEWER_NAME_SELECTOR)
        reviewer_name = (await name_el.inner_text()).strip() if name_el else None

        # Reviewer review count
        count_el = await card.query_selector(REVIEWER_COUNT_SELECTOR)
        reviewer_count = None
        if count_el:
            count_text = await count_el.inner_text()
            reviewer_count = _parse_review_count(count_text)

        # Date
        date_el = await card.query_selector(DATE_SELECTOR)
        posted_relative = None
        posted_at = None
        if date_el:
            posted_relative = (await date_el.inner_text()).strip()
            posted_at = _parse_relative_date(posted_relative)

        return ScrapedReview(
            content=content,
            star_rating=star_rating,
            reviewer_name=reviewer_name,
            reviewer_review_count=reviewer_count,
            posted_relative=posted_relative,
            posted_at=posted_at,
        )
    except Exception as e:
        logger.debug(f"Error extracting card: {e}")
        return None


async def scrape_restaurant(
    url: str,
    max_reviews: int = 100,
    progress_callback=None,   # async fn(progress: int, message: str)
) -> ScrapedRestaurant | None:
    """
    Scrape toàn bộ reviews của 1 quán từ Google Maps URL.

    Args:
        url: Google Maps URL
        max_reviews: Giới hạn số reviews scrape
        progress_callback: Async callback để update job progress
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
        )

        try:
            page = await context.new_page()

            if progress_callback:
                await progress_callback(5, "Đang mở Google Maps...")

            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            await _random_delay(2000, 3000)

            # Tên quán
            name_el = await page.query_selector(RESTAURANT_NAME_SELECTOR)
            restaurant_name = (await name_el.inner_text()).strip() if name_el else "Unknown"

            # Địa chỉ
            addr_el = await page.query_selector(RESTAURANT_ADDRESS_SELECTOR)
            address = (await addr_el.inner_text()).strip() if addr_el else None

            # Place ID
            place_id = parse_place_id_from_url(page.url) or parse_place_id_from_url(url)

            if progress_callback:
                await progress_callback(10, f"Tìm thấy: {restaurant_name}")

            # Click vào tab Reviews
            try:
                review_btn = await page.wait_for_selector(
                    REVIEWS_BUTTON_SELECTOR, timeout=5000
                )
                if review_btn:
                    await review_btn.click()
                    await _random_delay(1500, 2500)
            except Exception:
                logger.warning("Không tìm thấy nút Reviews — thử tiếp tục")

            if progress_callback:
                await progress_callback(15, "Đang tải reviews...")

            # Scroll để load thêm reviews
            max_scrolls = min(max_reviews // 10 + 5, 50)
            await _scroll_reviews_panel(page, max_scrolls=max_scrolls)

            if progress_callback:
                await progress_callback(40, "Đang trích xuất dữ liệu...")

            # Extract review cards
            cards = await page.query_selector_all(REVIEW_CARD_SELECTOR)
            reviews: list[ScrapedReview] = []

            for i, card in enumerate(cards[:max_reviews]):
                review = await _extract_review_card(card)
                if review:
                    reviews.append(review)

                if progress_callback and i % 10 == 0:
                    progress = 40 + int((i / min(len(cards), max_reviews)) * 30)
                    await progress_callback(progress, f"Đã xử lý {i}/{min(len(cards), max_reviews)} reviews...")

                await _random_delay(100, 300)

            logger.info(f"Scraped {len(reviews)} reviews from {restaurant_name}")

            return ScrapedRestaurant(
                name=restaurant_name,
                address=address,
                google_place_id=place_id,
                google_maps_url=url,
                reviews=reviews,
            )

        except Exception as e:
            logger.error(f"Scrape error: {e}")
            raise
        finally:
            await context.close()
            await browser.close()
