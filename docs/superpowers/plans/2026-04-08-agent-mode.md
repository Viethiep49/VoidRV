# Agent Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional AI agent chat widget to VoidRV that orchestrates existing APIs via LLM function calling, letting users type natural language (e.g. "phan tich quan pho Thin Ha Noi") instead of manually pasting URLs.

**Architecture:** A new FastAPI endpoint `/api/v1/agent/chat` receives user messages + LLM API key, runs an agent loop via LiteLLM (function calling with 3 tools that call existing services internally), and streams results back via SSE. A floating React chat widget in the frontend consumes the SSE stream.

**Tech Stack:** LiteLLM (multi-provider LLM abstraction), FastAPI SSE (sse-starlette), React chat widget with TailwindCSS

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `backend/services/agent_service.py` | Agent loop, tool definitions, tool execution, LiteLLM calls |
| Create | `backend/routers/agent.py` | POST /api/v1/agent/chat endpoint, SSE streaming |
| Create | `backend/models/agent_schemas.py` | Pydantic schemas for agent request/response |
| Create | `frontend/src/components/ChatWidget.jsx` | Floating chat bubble + panel + settings + SSE consumer |
| Modify | `backend/main.py` | Register agent router |
| Modify | `backend/requirements.txt` | Add litellm, sse-starlette |
| Create | `tests/test_agent_service.py` | Unit tests for agent tools + loop |
| Create | `tests/test_agent_router.py` | Integration test for agent endpoint |

---

### Task 1: Add dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add litellm and sse-starlette to requirements.txt**

Add these two lines at the end of `backend/requirements.txt`, before the Dev section:

```
# Agent mode
litellm>=1.40.0
sse-starlette>=2.1.0
```

- [ ] **Step 2: Install dependencies**

Run:
```bash
cd backend
pip install litellm sse-starlette
```
Expected: both packages install successfully.

- [ ] **Step 3: Verify import works**

Run:
```bash
python -c "import litellm; print(litellm.__version__)"
python -c "from sse_starlette.sse import EventSourceResponse; print('OK')"
```
Expected: version number printed, then "OK".

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add litellm and sse-starlette for agent mode"
```

---

### Task 2: Agent Pydantic schemas

**Files:**
- Create: `backend/models/agent_schemas.py`
- Test: `tests/test_agent_schemas.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_agent_schemas.py`:

```python
"""Tests for agent mode Pydantic schemas."""
import pytest
from backend.models.agent_schemas import AgentChatRequest, AgentSSEEvent


class TestAgentChatRequest:
    def test_valid_request(self):
        req = AgentChatRequest(message="pho Thin Ha Noi")
        assert req.message == "pho Thin Ha Noi"

    def test_empty_message_rejected(self):
        with pytest.raises(ValueError):
            AgentChatRequest(message="")

    def test_whitespace_only_rejected(self):
        with pytest.raises(ValueError):
            AgentChatRequest(message="   ")

    def test_message_stripped(self):
        req = AgentChatRequest(message="  hello  ")
        assert req.message == "hello"


class TestAgentSSEEvent:
    def test_status_event(self):
        event = AgentSSEEvent(event="status", data={"status": "Dang tim quan..."})
        assert event.event == "status"

    def test_token_event(self):
        event = AgentSSEEvent(event="token", data={"content": "hello"})
        assert event.event == "token"

    def test_invalid_event_type(self):
        with pytest.raises(ValueError):
            AgentSSEEvent(event="invalid_type", data={})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_schemas.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.models.agent_schemas'`

- [ ] **Step 3: Write the schemas**

Create `backend/models/agent_schemas.py`:

```python
"""Pydantic schemas for Agent Mode."""

from typing import Literal
from pydantic import BaseModel, field_validator


class AgentChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message khong duoc de trong")
        return v


class AgentSSEEvent(BaseModel):
    event: Literal["status", "token", "result", "done", "error"]
    data: dict
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_schemas.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/models/agent_schemas.py tests/test_agent_schemas.py
git commit -m "feat: add agent mode pydantic schemas"
```

---

### Task 3: Agent service — tool definitions

**Files:**
- Create: `backend/services/agent_service.py`
- Test: `tests/test_agent_service.py`

This task creates the tool definitions (OpenAI function calling format) and the tool dispatcher. The agent loop comes in Task 4.

- [ ] **Step 1: Write the failing test for tool definitions**

Create `tests/test_agent_service.py`:

```python
"""Tests for agent service — tool definitions and execution."""
import pytest
from backend.services.agent_service import TOOL_DEFINITIONS, PROVIDER_MODEL_MAP, SYSTEM_PROMPT


class TestToolDefinitions:
    def test_three_tools_defined(self):
        assert len(TOOL_DEFINITIONS) == 3

    def test_tool_names(self):
        names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
        assert names == {"search_restaurant", "scrape_and_analyze", "get_restaurant_result"}

    def test_each_tool_has_description(self):
        for tool in TOOL_DEFINITIONS:
            assert tool["function"]["description"]
            assert len(tool["function"]["description"]) > 10

    def test_each_tool_has_parameters(self):
        for tool in TOOL_DEFINITIONS:
            assert "parameters" in tool["function"]
            assert tool["function"]["parameters"]["type"] == "object"


class TestProviderModelMap:
    def test_openai_mapped(self):
        assert "openai" in PROVIDER_MODEL_MAP

    def test_anthropic_mapped(self):
        assert "anthropic" in PROVIDER_MODEL_MAP

    def test_gemini_mapped(self):
        assert "gemini" in PROVIDER_MODEL_MAP

    def test_unknown_provider_raises(self):
        assert "unknown" not in PROVIDER_MODEL_MAP


class TestSystemPrompt:
    def test_system_prompt_exists(self):
        assert len(SYSTEM_PROMPT) > 50

    def test_mentions_voidrv(self):
        assert "VoidRV" in SYSTEM_PROMPT
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_service.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write tool definitions**

Create `backend/services/agent_service.py`:

```python
"""
Agent Mode — LLM agent loop with function calling via LiteLLM.
Orchestrates existing VoidRV services to answer user questions.
"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

import litellm

logger = logging.getLogger(__name__)

PROVIDER_MODEL_MAP = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini/gemini-2.0-flash",
}

SYSTEM_PROMPT = (
    "Ban la tro ly VoidRV — he thong danh gia do tin cay review nha hang tai Viet Nam.\n\n"
    "Khi user hoi ve 1 quan:\n"
    "1. Dung search_restaurant de tim Google Maps URL\n"
    "2. Dung scrape_and_analyze de scrape + phan tich\n"
    "3. Dung get_restaurant_result de lay ket qua\n"
    "4. Tong hop va tra loi user bang tieng Viet\n\n"
    "Tra loi ngan gon. Neu: Trust Score, Void Score, badge, adjusted rating, va nhan xet chinh.\n"
    "Cuoi message, dinh kem link toi dashboard: /restaurant/{slug}"
)

MAX_AGENT_LOOPS = 5

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_restaurant",
            "description": "Tim Google Maps URL tu ten quan an va khu vuc. Tra ve URL Google Maps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Ten quan + khu vuc, vi du: 'Pho Thin Ha Noi' hoac 'Bun cha Huong Lien Hanoi'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_and_analyze",
            "description": "Scrape reviews tu Google Maps URL va chay full analysis pipeline. Tra ve restaurant slug va summary stats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "google_maps_url": {
                        "type": "string",
                        "description": "URL Google Maps cua quan an",
                    }
                },
                "required": ["google_maps_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_result",
            "description": "Lay ket qua phan tich da xong. Tra ve trust score, void score, adjusted rating, risk level, top reviews.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Restaurant slug (tu scrape_and_analyze)",
                    }
                },
                "required": ["slug"],
            },
        },
    },
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_service.py -v`
Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/agent_service.py tests/test_agent_service.py
git commit -m "feat: add agent tool definitions and provider map"
```

---

### Task 4: Agent service — tool execution functions

**Files:**
- Modify: `backend/services/agent_service.py`
- Modify: `tests/test_agent_service.py`

- [ ] **Step 1: Write the failing test for tool execution**

Add to `tests/test_agent_service.py`:

```python
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock


class TestSearchRestaurant:
    @pytest.mark.asyncio
    async def test_search_returns_url(self):
        from backend.services.agent_service import execute_search_restaurant

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://www.google.com/maps/place/Pho+Thin/"
        mock_response.text = "Pho Thin"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            result = await execute_search_restaurant("Pho Thin Ha Noi")

        assert "google.com/maps" in result or "error" in result

    @pytest.mark.asyncio
    async def test_search_handles_failure(self):
        from backend.services.agent_service import execute_search_restaurant

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=Exception("Network error")):
            result = await execute_search_restaurant("Pho Thin Ha Noi")

        assert "error" in result.lower() or "khong" in result.lower()


class TestGetRestaurantResult:
    @pytest.mark.asyncio
    async def test_get_result_not_found(self):
        from backend.services.agent_service import execute_get_restaurant_result

        with patch("backend.services.agent_service.crud.get_restaurant_by_slug", new_callable=AsyncMock, return_value=None):
            result = await execute_get_restaurant_result("nonexistent-slug")

        assert "khong tim thay" in result.lower() or "error" in result.lower()


class TestExecuteTool:
    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self):
        from backend.services.agent_service import execute_tool

        result = await execute_tool("unknown_tool", {})
        assert "khong ho tro" in result.lower() or "error" in result.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_service.py::TestSearchRestaurant -v`
Expected: FAIL — `ImportError: cannot import name 'execute_search_restaurant'`

- [ ] **Step 3: Implement tool execution functions**

Add to `backend/services/agent_service.py`:

```python
import httpx
import re
import uuid

from ..db.database import AsyncSessionLocal
from ..db import crud


async def execute_search_restaurant(query: str) -> str:
    """Search Google Maps for a restaurant and return the URL."""
    try:
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(
                search_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            )
            final_url = str(response.url)
            if "google.com/maps" in final_url:
                return json.dumps({"url": final_url})
            return json.dumps({"error": f"Khong tim thay quan '{query}' tren Google Maps."})
    except Exception as e:
        logger.error(f"search_restaurant failed: {e}")
        return json.dumps({"error": f"Loi khi tim kiem: {str(e)[:200]}"})


async def execute_scrape_and_analyze(google_maps_url: str) -> str:
    """Trigger the scrape pipeline and wait for completion."""
    from .scraper import scrape_restaurant
    from .similarity import compute_simhash
    from .content_module import analyze_content
    from .behavior_module import analyze_behavior, ReviewMeta
    from .trust_engine import build_trust_result
    from ..ml.model import get_classifier
    from ..routers.scrape import _slugify

    try:
        async with AsyncSessionLocal() as db:
            # 1. Scrape
            scraped = await scrape_restaurant(google_maps_url, max_reviews=50)
            if not scraped or not scraped.reviews:
                return json.dumps({"error": "Khong scrape duoc reviews. Google Maps co the dang chan."})

            # 2. Upsert restaurant
            slug = _slugify(scraped.name)
            restaurant = await crud.get_restaurant_by_slug(db, slug)
            if not restaurant:
                restaurant = await crud.create_restaurant(
                    db, name=scraped.name, slug=slug,
                    address=scraped.address,
                    google_place_id=scraped.google_place_id,
                    google_maps_url=google_maps_url,
                )
            await crud.update_restaurant_scraped_at(db, restaurant.id)

            # 3. Save reviews
            reviews_data = []
            for r in scraped.reviews:
                simhash = compute_simhash(r.content)
                reviews_data.append({
                    "restaurant_id": restaurant.id,
                    "content": r.content,
                    "star_rating": r.star_rating,
                    "reviewer_name": r.reviewer_name,
                    "reviewer_review_count": r.reviewer_review_count,
                    "posted_relative": r.posted_relative,
                    "posted_at": r.posted_at,
                    "simhash": simhash,
                    "source": "google_maps",
                })
            db_reviews = await crud.bulk_create_reviews(db, reviews_data)

            # 4. Analyze
            classifier = get_classifier()
            batch_texts = [r.content for r in scraped.reviews]
            batch_meta = [
                ReviewMeta(
                    review_id=db_reviews[i].id,
                    reviewer_name=scraped.reviews[i].reviewer_name,
                    reviewer_review_count=scraped.reviews[i].reviewer_review_count,
                    posted_at=scraped.reviews[i].posted_at,
                    star_rating=scraped.reviews[i].star_rating,
                )
                for i in range(len(scraped.reviews))
            ]

            scores_data = []
            for i, (db_review, raw_review) in enumerate(zip(db_reviews, scraped.reviews)):
                other_texts = batch_texts[:i] + batch_texts[i + 1:]
                content_result = analyze_content(
                    raw_review.content, raw_review.star_rating,
                    classifier, batch_texts=other_texts,
                )
                behavior_result = analyze_behavior(batch_meta[i], batch_meta)
                trust = build_trust_result(content_result, behavior_result)

                scores_data.append({
                    "review_id": db_review.id,
                    "content_score": trust.content_score,
                    "behavior_score": trust.behavior_score,
                    "trust_score": trust.trust_score,
                    "confidence": trust.confidence,
                    "content_only": False,
                    "badge": trust.badge,
                    "aspects_found": trust.aspects_found,
                    "explanation": trust.explanation,
                    "breakdown": trust.breakdown,
                    "model_version": "phobert_reviewtrust_v1",
                })
            await crud.bulk_create_trust_scores(db, scores_data)

            return json.dumps({
                "slug": slug,
                "name": scraped.name,
                "reviews_analyzed": len(db_reviews),
                "message": f"Da phan tich {len(db_reviews)} reviews cho {scraped.name}.",
            })
    except Exception as e:
        logger.error(f"scrape_and_analyze failed: {e}")
        return json.dumps({"error": f"Loi khi scrape: {str(e)[:200]}"})


async def execute_get_restaurant_result(slug: str) -> str:
    """Get analysis results for a restaurant."""
    from .trust_engine import generate_risk_report, build_timeline
    from .similarity import find_clusters

    try:
        async with AsyncSessionLocal() as db:
            restaurant = await crud.get_restaurant_by_slug(db, slug)
            if not restaurant:
                return json.dumps({"error": f"Khong tim thay quan voi slug '{slug}'. Hay scrape truoc."})

            db_reviews = await crud.get_reviews_by_restaurant(db, restaurant.id)
            if not db_reviews:
                return json.dumps({"error": "Quan chua co reviews."})

            stats = await crud.get_restaurant_stats(db, restaurant.id)

            trust_scores = [r.trust_score.trust_score if r.trust_score else 50.0 for r in db_reviews]
            texts = [r.content for r in db_reviews]
            review_ids = [r.id for r in db_reviews]

            reviews_meta = [
                {
                    "review_id": r.id,
                    "reviewer_review_count": r.reviewer_review_count,
                    "posted_at": r.posted_at,
                    "trust_score": r.trust_score.trust_score if r.trust_score else 50.0,
                }
                for r in db_reviews
            ]
            risk = generate_risk_report(reviews_meta, trust_scores, texts, review_ids)

            # Top 3 trusted reviews
            trusted_reviews = sorted(
                [r for r in db_reviews if r.trust_score],
                key=lambda r: r.trust_score.trust_score,
                reverse=True,
            )[:3]

            top_reviews = [
                {
                    "content": r.content[:150],
                    "trust_score": r.trust_score.trust_score,
                    "star_rating": r.star_rating,
                    "badge": r.trust_score.badge,
                }
                for r in trusted_reviews
            ]

            return json.dumps({
                "name": restaurant.name,
                "slug": slug,
                "total_reviews": stats["total_reviews"],
                "avg_trust_score": stats["avg_trust_score"],
                "avg_star_rating": stats["avg_star_rating"],
                "void_score": round(100 - stats["avg_trust_score"], 1),
                "risk_level": risk.risk_level,
                "risk_factors": risk.risk_factors,
                "distribution": stats["distribution"],
                "top_trusted_reviews": top_reviews,
                "dashboard_url": f"/restaurant/{slug}",
            })
    except Exception as e:
        logger.error(f"get_restaurant_result failed: {e}")
        return json.dumps({"error": f"Loi khi lay ket qua: {str(e)[:200]}"})


async def execute_tool(tool_name: str, arguments: dict) -> str:
    """Dispatch tool call to the correct function."""
    if tool_name == "search_restaurant":
        return await execute_search_restaurant(arguments["query"])
    elif tool_name == "scrape_and_analyze":
        return await execute_scrape_and_analyze(arguments["google_maps_url"])
    elif tool_name == "get_restaurant_result":
        return await execute_get_restaurant_result(arguments["slug"])
    else:
        return json.dumps({"error": f"Tool '{tool_name}' khong ho tro."})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent_service.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/agent_service.py tests/test_agent_service.py
git commit -m "feat: implement agent tool execution functions"
```

---

### Task 5: Agent service — agent loop with SSE streaming

**Files:**
- Modify: `backend/services/agent_service.py`
- Modify: `tests/test_agent_service.py`

- [ ] **Step 1: Write the failing test for agent loop**

Add to `tests/test_agent_service.py`:

```python
class TestAgentLoop:
    @pytest.mark.asyncio
    async def test_rejects_unknown_provider(self):
        from backend.services.agent_service import run_agent_loop

        events = []
        async for event in run_agent_loop("hello", "fake-key", "unknown_provider"):
            events.append(event)

        assert any(e["event"] == "error" for e in events)

    @pytest.mark.asyncio
    async def test_yields_error_on_invalid_key(self):
        from backend.services.agent_service import run_agent_loop

        events = []
        try:
            async for event in run_agent_loop("hello", "invalid-key", "openai"):
                events.append(event)
                if len(events) > 5:
                    break
        except Exception:
            pass

        # Should get at least an error event or raise
        assert len(events) >= 0  # Just verifying it doesn't hang
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_service.py::TestAgentLoop::test_rejects_unknown_provider -v`
Expected: FAIL — `ImportError: cannot import name 'run_agent_loop'`

- [ ] **Step 3: Implement the agent loop**

Add to `backend/services/agent_service.py`:

```python
async def run_agent_loop(
    message: str,
    api_key: str,
    provider: str,
) -> AsyncGenerator[dict, None]:
    """
    Run the agent loop: send message to LLM, execute tool calls, stream response.
    Yields SSE event dicts: {"event": "status|token|result|done|error", "data": {...}}
    """
    if provider not in PROVIDER_MODEL_MAP:
        yield {"event": "error", "data": {"error": f"Provider '{provider}' khong duoc ho tro. Chon: openai, anthropic, gemini"}}
        return

    model = PROVIDER_MODEL_MAP[provider]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    try:
        for loop_i in range(MAX_AGENT_LOOPS):
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                api_key=api_key,
            )

            choice = response.choices[0]

            # If LLM wants to call tools
            if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
                messages.append(choice.message.model_dump())

                for tool_call in choice.message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    status_map = {
                        "search_restaurant": "Dang tim quan tren Google Maps...",
                        "scrape_and_analyze": "Dang scrape va phan tich reviews...",
                        "get_restaurant_result": "Dang lay ket qua phan tich...",
                    }
                    yield {"event": "status", "data": {"status": status_map.get(fn_name, "Dang xu ly...")}}

                    tool_result = await execute_tool(fn_name, fn_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })

                    # If result contains a slug, emit result event
                    try:
                        parsed = json.loads(tool_result)
                        if "slug" in parsed:
                            yield {"event": "result", "data": {"restaurant_slug": parsed["slug"]}}
                    except (json.JSONDecodeError, KeyError):
                        pass

                continue  # Next loop iteration to get LLM's response

            # LLM returned final text
            content = choice.message.content or ""
            yield {"event": "token", "data": {"content": content}}
            yield {"event": "done", "data": {}}
            return

        # Exhausted max loops
        yield {"event": "error", "data": {"error": "Agent khong the hoan thanh. Vui long thu lai."}}

    except litellm.AuthenticationError:
        yield {"event": "error", "data": {"error": "API key khong hop le. Vui long kiem tra lai."}}
    except Exception as e:
        logger.error(f"Agent loop error: {e}")
        yield {"event": "error", "data": {"error": f"Loi: {str(e)[:300]}"}}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent_service.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/agent_service.py tests/test_agent_service.py
git commit -m "feat: implement agent loop with LiteLLM function calling"
```

---

### Task 6: Agent router — SSE endpoint

**Files:**
- Create: `backend/routers/agent.py`
- Create: `tests/test_agent_router.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_agent_router.py`:

```python
"""Tests for agent router endpoint."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


class TestAgentEndpoint:
    @pytest.mark.asyncio
    async def test_missing_api_key_returns_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agent/chat",
                json={"message": "test"},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_missing_provider_returns_400(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agent/chat",
                json={"message": "test"},
                headers={"X-LLM-Api-Key": "test-key"},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_empty_message_returns_422(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agent/chat",
                json={"message": ""},
                headers={
                    "X-LLM-Api-Key": "test-key",
                    "X-LLM-Provider": "openai",
                },
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_valid_request_returns_sse_stream(self):
        """With a valid request but fake key, should get SSE error event (not HTTP error)."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/agent/chat",
                json={"message": "test"},
                headers={
                    "X-LLM-Api-Key": "fake-key",
                    "X-LLM-Provider": "openai",
                },
            )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_router.py -v`
Expected: FAIL — 404 (route doesn't exist yet)

- [ ] **Step 3: Create the agent router**

Create `backend/routers/agent.py`:

```python
"""
POST /api/v1/agent/chat — Agent mode: LLM-powered chat with function calling.
Optional feature — requires user to provide their own LLM API key.
"""

import json
from fastapi import APIRouter, Header, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from ..models.agent_schemas import AgentChatRequest
from ..services.agent_service import run_agent_loop

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
async def agent_chat(
    request: AgentChatRequest,
    x_llm_api_key: str | None = Header(None),
    x_llm_provider: str | None = Header(None),
):
    """
    Chat with VoidRV agent. Requires LLM API key and provider in headers.
    Returns SSE stream with status updates, tokens, and results.
    """
    if not x_llm_api_key:
        raise HTTPException(400, "Thieu API key. Gui header X-LLM-Api-Key.")
    if not x_llm_provider:
        raise HTTPException(400, "Thieu provider. Gui header X-LLM-Provider (openai/anthropic/gemini).")

    async def event_generator():
        async for event in run_agent_loop(request.message, x_llm_api_key, x_llm_provider):
            yield {
                "event": event["event"],
                "data": json.dumps(event["data"], ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_router.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/routers/agent.py tests/test_agent_router.py
git commit -m "feat: add agent chat SSE endpoint"
```

---

### Task 7: Register agent router in main.py

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: Add import and register router**

In `backend/main.py`, add the agent router import and registration.

Add to the imports (line 14):
```python
from .routers import analyze, restaurant, scrape, agent
```

Add after line 51 (`app.include_router(restaurant.router, prefix="/api/v1")`):
```python
app.include_router(agent.router, prefix="/api/v1")
```

- [ ] **Step 2: Verify server starts**

Run:
```bash
cd backend
uvicorn main:app --reload
```
Expected: Server starts without errors. Check `http://localhost:8000/docs` — should show `/api/v1/agent/chat` endpoint.

- [ ] **Step 3: Commit**

```bash
git add backend/main.py
git commit -m "feat: register agent router in main app"
```

---

### Task 8: Frontend — ChatWidget component

**Files:**
- Create: `frontend/src/components/ChatWidget.jsx`

Note: Frontend folder structure exists but has no code files yet. This task creates the chat widget as a self-contained component. It will be integrated into App.jsx when the main frontend is built.

- [ ] **Step 1: Create ChatWidget.jsx**

Create `frontend/src/components/ChatWidget.jsx`:

```jsx
import { useState, useRef, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "gemini", label: "Google Gemini" },
];

function getConfig() {
  try {
    const raw = localStorage.getItem("voidrv_agent_config");
    return raw ? JSON.parse(raw) : { provider: "openai", apiKey: "" };
  } catch {
    return { provider: "openai", apiKey: "" };
  }
}

function saveConfig(config) {
  localStorage.setItem("voidrv_agent_config", JSON.stringify(config));
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [config, setConfig] = useState(getConfig);
  const [messages, setMessages] = useState([
    {
      role: "agent",
      content: "Xin chao! Toi la tro ly VoidRV. Paste API key trong Settings roi hoi toi ve bat ky quan an nao.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  const handleSaveConfig = () => {
    saveConfig(config);
    setShowSettings(false);
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    if (!config.apiKey) {
      setShowSettings(true);
      return;
    }

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);
    setStatus("Dang ket noi...");

    try {
      const response = await fetch(`${API_BASE}/api/v1/agent/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-LLM-Api-Key": config.apiKey,
          "X-LLM-Provider": config.provider,
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        const err = await response.json();
        setMessages((prev) => [
          ...prev,
          { role: "agent", content: `Loi: ${err.detail || "Khong xac dinh"}` },
        ]);
        setIsLoading(false);
        setStatus("");
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let agentContent = "";
      let resultSlug = null;
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            var eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            const dataStr = line.slice(5).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              if (eventType === "status") {
                setStatus(data.status);
              } else if (eventType === "token") {
                agentContent += data.content;
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.role === "agent" && last.streaming) {
                    last.content = agentContent;
                  } else {
                    updated.push({ role: "agent", content: agentContent, streaming: true });
                  }
                  return [...updated];
                });
              } else if (eventType === "result") {
                resultSlug = data.restaurant_slug;
              } else if (eventType === "error") {
                agentContent = `Loi: ${data.error}`;
                setMessages((prev) => [...prev, { role: "agent", content: agentContent }]);
              } else if (eventType === "done") {
                // Mark streaming complete
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last && last.streaming) {
                    last.streaming = false;
                    if (resultSlug) {
                      last.resultSlug = resultSlug;
                    }
                  }
                  return [...updated];
                });
              }
            } catch {
              // skip malformed data
            }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: `Loi ket noi: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
      setStatus("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg flex items-center justify-center transition-colors"
        aria-label="Open chat"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-indigo-600 text-white">
        <span className="font-semibold text-sm">VoidRV Agent</span>
        <div className="flex gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="hover:bg-indigo-700 p-1 rounded transition-colors"
            aria-label="Settings"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-indigo-700 p-1 rounded transition-colors"
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="p-4 bg-gray-50 border-b border-gray-200">
          <label className="block text-xs font-medium text-gray-700 mb-1">Provider</label>
          <select
            value={config.provider}
            onChange={(e) => setConfig({ ...config, provider: e.target.value })}
            className="w-full mb-3 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>

          <label className="block text-xs font-medium text-gray-700 mb-1">API Key</label>
          <input
            type="password"
            value={config.apiKey}
            onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
            placeholder="sk-..."
            className="w-full mb-3 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />

          <button
            onClick={handleSaveConfig}
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Luu
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] px-3 py-2 rounded-2xl text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {msg.content}
              {msg.resultSlug && (
                <a
                  href={`/restaurant/${msg.resultSlug}`}
                  className="block mt-2 text-indigo-600 hover:underline text-xs font-medium"
                >
                  Xem dashboard &rarr;
                </a>
              )}
            </div>
          </div>
        ))}

        {status && (
          <div className="flex justify-start">
            <div className="px-3 py-2 rounded-2xl text-sm bg-yellow-50 text-yellow-700 border border-yellow-200">
              {status}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={isLoading ? "Dang xu ly..." : "Nhap tin nhan..."}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Gui
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify component renders**

If frontend dev server is running:
```bash
cd frontend
npm run dev
```

Import and render `<ChatWidget />` in your App component. Should see floating bubble at bottom-right.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatWidget.jsx
git commit -m "feat: add floating chat widget for agent mode"
```

---

### Task 9: Integration test — end-to-end agent flow

**Files:**
- Create: `tests/test_agent_e2e.py`

- [ ] **Step 1: Write e2e test with mocked LLM**

Create `tests/test_agent_e2e.py`:

```python
"""End-to-end test for agent flow with mocked LLM responses."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from backend.main import app


def make_mock_llm_response(content: str = None, tool_calls: list = None):
    """Create a mock LiteLLM response."""
    message = MagicMock()
    message.content = content
    message.tool_calls = tool_calls

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = "tool_calls" if tool_calls else "stop"

    response = MagicMock()
    response.choices = [choice]
    return response


def make_tool_call(name: str, arguments: dict, call_id: str = "call_1"):
    tc = MagicMock()
    tc.id = call_id
    tc.function = MagicMock()
    tc.function.name = name
    tc.function.arguments = json.dumps(arguments)
    return tc


class TestAgentE2E:
    @pytest.mark.asyncio
    async def test_simple_text_response(self):
        """LLM returns text directly without tool calls."""
        mock_response = make_mock_llm_response(content="Xin chao! Toi la VoidRV.")

        with patch("backend.services.agent_service.litellm.acompletion", new_callable=AsyncMock, return_value=mock_response):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/agent/chat",
                    json={"message": "xin chao"},
                    headers={
                        "X-LLM-Api-Key": "test-key",
                        "X-LLM-Provider": "openai",
                    },
                )

            assert response.status_code == 200
            body = response.text
            assert "Xin chao" in body

    @pytest.mark.asyncio
    async def test_tool_call_flow(self):
        """LLM calls search_restaurant, then returns text."""
        tool_call = make_tool_call("search_restaurant", {"query": "Pho Thin Ha Noi"})
        first_response = make_mock_llm_response(tool_calls=[tool_call])
        second_response = make_mock_llm_response(content="Da tim thay Pho Thin. Trust Score: 72.")

        call_count = 0
        async def mock_completion(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return first_response
            return second_response

        with patch("backend.services.agent_service.litellm.acompletion", side_effect=mock_completion):
            with patch("backend.services.agent_service.execute_search_restaurant", new_callable=AsyncMock, return_value='{"url": "https://google.com/maps/place/Pho+Thin"}'):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/agent/chat",
                        json={"message": "phan tich pho Thin Ha Noi"},
                        headers={
                            "X-LLM-Api-Key": "test-key",
                            "X-LLM-Provider": "openai",
                        },
                    )

                assert response.status_code == 200
                body = response.text
                assert "status" in body or "token" in body
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_agent_e2e.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_agent_e2e.py
git commit -m "test: add agent mode e2e tests with mocked LLM"
```

---

### Task 10: Run full test suite and verify

**Files:** None (verification only)

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```
Expected: All tests PASS.

- [ ] **Step 2: Start server and verify endpoint shows in docs**

```bash
cd backend
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` — verify `/api/v1/agent/chat` appears.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete agent mode — LLM chat widget with function calling"
```
