# VoidRV Agent Mode — Design Spec

**Date:** 2026-04-08
**Status:** Draft
**Author:** Brainstorming session

---

## Overview

Thêm optional Agent Mode cho VoidRV: chat widget floating cho phép user nhắn tự nhiên (ví dụ "phân tích quán phở Thìn Hà Nội"), một LLM agent tự orchestrate các API có sẵn để tìm quán, scrape, phân tích, và trả kết quả.

**Nguyên tắc:** Core engine hoàn toàn không bị sửa. Agent mode chỉ là consumer layer gọi lại các service có sẵn. Không có agent thì hệ thống vẫn hoạt động bình thường.

---

## Architecture

```
┌─────────────────────────────────────┐
│  Frontend (React)                   │
│  ┌───────────────────────────────┐  │
│  │ ChatWidget (floating bubble)  │  │
│  │  - localStorage: API key      │  │
│  │  - POST /api/v1/agent/chat    │  │
│  │  - SSE stream response        │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │ Header: X-LLM-Api-Key + X-LLM-Provider
               ▼
┌─────────────────────────────────────┐
│  Backend (FastAPI)                  │
│  ┌───────────────────────────────┐  │
│  │ routers/agent.py              │  │
│  │  POST /api/v1/agent/chat      │  │
│  └──────────┬────────────────────┘  │
│             ▼                       │
│  ┌───────────────────────────────┐  │
│  │ services/agent_service.py     │  │
│  │  - LiteLLM call (function     │  │
│  │    calling / tool use)        │  │
│  │  - Agent loop: LLM → tool    │  │
│  │    → LLM → ... → final       │  │
│  │  - 3 tools (see below)        │  │
│  └───────────────────────────────┘  │
│             │                       │
│             ▼ (internal calls)      │
│  ┌───────────────────────────────┐  │
│  │ Existing core engine          │  │
│  │  scraper → content_module     │  │
│  │  → behavior_module            │  │
│  │  → trust_engine → DB          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Backend

### New files

| File | Purpose |
|------|---------|
| `backend/routers/agent.py` | POST /api/v1/agent/chat endpoint |
| `backend/services/agent_service.py` | Agent loop + tool definitions + LiteLLM integration |

### Endpoint

```
POST /api/v1/agent/chat
Headers:
  X-LLM-Api-Key: <user's API key>
  X-LLM-Provider: openai | anthropic | gemini
Body:
  { "message": "phân tích quán phở Thìn Hà Nội" }
Response:
  SSE stream (text/event-stream)
```

### SSE Event Types

```
event: status
data: {"status": "Đang tìm quán..."}

event: token
data: {"content": "Kết quả phân tích..."}

event: result
data: {"restaurant_slug": "pho-thin", "trust_score": 72.5}

event: done
data: {}

event: error
data: {"error": "API key không hợp lệ"}
```

### Agent Tools (3 tools)

| Tool | Description | Internal call |
|------|-------------|---------------|
| `search_restaurant` | Tìm Google Maps URL từ tên quán. Input: tên quán + khu vực. Output: Google Maps URL. | httpx GET `https://www.google.com/maps/search/{query}` → parse URL từ response. Nếu không tìm được → trả error message cho LLM tự thông báo user. |
| `scrape_and_analyze` | Scrape reviews từ Google Maps URL + chạy full analysis pipeline. Input: Google Maps URL. Output: restaurant slug + summary stats. | Gọi `_run_scrape_pipeline()` trực tiếp (không qua HTTP), await completion |
| `get_restaurant_result` | Lấy kết quả phân tích đã xong. Input: restaurant slug. Output: trust score, void score, adjusted rating, top reviews, risk level. | Gọi `crud.get_restaurant_stats()` + `generate_risk_report()` |

### Agent Loop

```python
# Pseudocode
def agent_chat(message, api_key, provider):
    messages = [system_prompt, user_message]

    for i in range(MAX_LOOPS := 5):
        response = litellm.completion(
            model=provider_model_map[provider],
            messages=messages,
            tools=TOOL_DEFINITIONS,
            api_key=api_key,
            stream=True,
        )

        if response has tool_calls:
            for tool_call in tool_calls:
                yield SSE status event
                result = execute_tool(tool_call)
                messages.append(tool_result)
        else:
            yield SSE token events (streamed)
            break
```

### System Prompt

```
Bạn là trợ lý VoidRV — hệ thống đánh giá độ tin cậy review nhà hàng tại Việt Nam.

Khi user hỏi về 1 quán:
1. Dùng search_restaurant để tìm Google Maps URL
2. Dùng scrape_and_analyze để scrape + phân tích
3. Dùng get_restaurant_result để lấy kết quả
4. Tổng hợp và trả lời user bằng tiếng Việt

Trả lời ngắn gọn. Nêu: Trust Score, Void Score, badge, adjusted rating, và nhận xét chính.
Cuối message, đính kèm link tới dashboard: /restaurant/{slug}
```

### Dependency

Thêm vào `requirements.txt`:
```
litellm>=1.40.0
```

### Error Handling

| Error | Response |
|-------|----------|
| Thiếu API key | SSE error: "Vui lòng cung cấp API key trong Settings" |
| API key invalid | SSE error: "API key không hợp lệ. Vui lòng kiểm tra lại." |
| Provider không hỗ trợ | SSE error: "Provider không được hỗ trợ. Chọn: openai, anthropic, gemini" |
| Scrape thất bại | Agent nhận error từ tool, tự trả lời user "Không scrape được, thử lại sau" |
| Max loops reached | SSE error: "Agent không thể hoàn thành. Vui lòng thử lại." |

---

## Frontend

### New files

| File | Purpose |
|------|---------|
| `frontend/src/components/ChatWidget.jsx` | Floating chat widget component |
| `frontend/src/components/ChatWidget.css` | Styles (hoặc dùng Tailwind inline) |

### UI Layout

```
┌──────────────────────────────┐
│ VoidRV Agent          ⚙ ✕  │  ← Header: title + settings + close
├──────────────────────────────┤
│                              │
│  ○ Xin chào! Paste API key  │  ← Agent welcome message
│    trong Settings để bắt đầu│
│                              │
│         phở Thìn Hà Nội  ●  │  ← User message (right)
│                              │
│  ○ Đang tìm quán...         │  ← Status indicator
│  ○ Trust Score: 68/100       │  ← Agent response (left)
│    Badge: Cần thận trọng     │
│    → Xem dashboard           │
│                              │
├──────────────────────────────┤
│ Nhập tin nhắn...      [Send]│  ← Input + send button
└──────────────────────────────┘

   [💬]  ← Floating bubble (góc phải dưới)
```

### Settings Panel (toggle in widget)

```
┌──────────────────────────────┐
│ Settings                  ✕  │
├──────────────────────────────┤
│ Provider:                    │
│ [OpenAI     ▼]               │
│                              │
│ API Key:                     │
│ [sk-xxxxxxxxxxxxx]           │
│                              │
│ [Lưu]                       │
└──────────────────────────────┘
```

- Lưu vào `localStorage` key `voidrv_agent_config`:
  ```json
  { "provider": "openai", "apiKey": "sk-..." }
  ```

### Behavior

- Floating bubble hiện trên mọi trang
- Click bubble → toggle chat panel
- Chưa có API key → hiện welcome message hướng dẫn vào Settings
- Gửi message → disable input, hiện typing indicator
- Stream response → render từng chunk real-time
- Kết quả có link `/restaurant/:slug` → click navigate tới dashboard
- Refresh page → mất chat history (không persist)
- Không hỗ trợ multi-conversation

### Provider → Model Map

| Provider | Model |
|----------|-------|
| openai | gpt-4o-mini |
| anthropic | claude-haiku-4-5-20251001 |
| gemini | gemini/gemini-2.0-flash |

Dùng model rẻ/nhanh vì task đơn giản (orchestration, không cần deep reasoning).

---

## Scope — Không làm

- Không lưu chat history vào DB
- Không cần user account / authentication
- Không so sánh nhiều quán (chỉ 1 quán per conversation)
- Không file upload
- Không voice input
- Không custom system prompt
- Không rate limiting (đồ án)

---

## Files Changed (summary)

### New files
- `backend/routers/agent.py`
- `backend/services/agent_service.py`
- `frontend/src/components/ChatWidget.jsx`

### Modified files
- `backend/main.py` — thêm `include_router(agent.router)`
- `backend/requirements.txt` — thêm `litellm`
- `frontend/src/App.jsx` — render `<ChatWidget />` globally
