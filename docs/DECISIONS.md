# Technical Decisions

This document records important architectural and technical decisions made during development. Future AI coding agents should respect these decisions unless there's a critical reason to change them.

---

## Decision 1: FastAPI over Flask/Django
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to choose Python web framework for the backend API.

### Options Considered
1. **Flask** - Lightweight, simple, mature
2. **Django** - Full-featured, batteries-included, ORM built-in
3. **FastAPI** - Modern, async, automatic API docs

### Decision
Choose **FastAPI**

### Rationale
- **Async Support**: Native async/await for I/O operations (LLM calls, web scraping)
- **Performance**: Faster than Flask/Django due to async nature
- **Type Safety**: Automatic validation using Pydantic
- **API Documentation**: Automatic OpenAPI/Swagger docs generation
- **Modern**: Built on modern Python standards (type hints, async)
- **Developer Experience**: Better autocomplete and error detection

### Consequences
- Learning curve for developers unfamiliar with async Python
- Requires Python 3.7+ (we're using 3.11+)
- Must use async database drivers (asyncpg)

---

## Decision 2: Playwright + HTTPX Hybrid Scraping
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to scrape both static HTML and JavaScript-rendered pages.

### Options Considered
1. **Requests only** - Simple, fast, but no JS support
2. **Selenium** - Full browser, heavy resource usage
3. **Playwright** - Modern browser automation, faster than Selenium
4. **HTTPX + Playwright hybrid** - Use HTTPX for static, Playwright for JS

### Decision
Use **HTTPX for static pages, Playwright for JS-rendered pages**

### Rationale
- **Efficiency**: HTTPX is faster and lighter for static pages
- **Capability**: Playwright handles JavaScript-heavy sites
- **Resource Optimization**: Only use browser when necessary
- **Modern**: Playwright is actively maintained, faster than Selenium
- **Async Support**: Both support async operations

### Implementation
```python
def select_scraper(url: str) -> Scraper:
    if requires_javascript(url):
        return BrowserScraper(playwright)
    else:
        return HTTPScraper(httpx)
```

### Consequences
- Need to detect when JavaScript rendering is needed
- Playwright requires Chromium installation (~200MB)
- Docker image will be larger

---

## Decision 3: Groq as Primary LLM Provider
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to choose primary LLM provider for natural language understanding and extraction schema generation.

### Options Considered
1. **OpenAI GPT-4** - Most powerful, but expensive
2. **Anthropic Claude** - Strong reasoning, moderate pricing
3. **Groq** - Fast inference, cost-effective, good quality
4. **Google Gemini** - Generous free tier, good quality
5. **Local LLMs** - Free but requires GPU

### Decision
Use **Groq as primary, Gemini as fallback**

### Rationale
**Groq Advantages**:
- **Speed**: Sub-second inference (~0.5s typical)
- **Cost**: Very competitive pricing
- **Quality**: Mixtral and Llama models are high-quality
- **JSON Mode**: Native structured output support
- **Reliability**: Good uptime

**Gemini as Fallback**:
- **Free Tier**: Generous quota for testing
- **Rate Limits**: Higher than Groq for fallback scenarios
- **Quality**: Good performance on structured tasks
- **Availability**: Google infrastructure reliability

### Consequences
- Need API keys for both services
- Must implement fallback logic
- Different response formats to normalize

---

## Decision 4: Provider-Agnostic LLM Architecture
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Want to avoid vendor lock-in and enable easy provider switching.

### Decision
Implement **abstract LLM provider interface** with factory pattern

### Rationale
- **Flexibility**: Easy to add new providers (OpenAI, Claude, local)
- **Reliability**: Automatic fallback on primary provider failure
- **Testing**: Easy to mock providers for tests
- **Maintenance**: Provider-specific code is isolated
- **Evolution**: Can optimize per-provider without affecting others

### Implementation
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_extraction_schema(...)
    
    @abstractmethod
    async def identify_page_structure(...)

class GroqProvider(LLMProvider):
    # Groq-specific implementation

class GeminiProvider(LLMProvider):
    # Gemini-specific implementation
```

### Consequences
- More initial code to write
- Abstraction layer overhead (minimal)
- Easier long-term maintenance

---

## Decision 5: PostgreSQL over MongoDB
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to choose database for storing extraction jobs and results.

### Options Considered
1. **PostgreSQL** - Relational, ACID, JSONB support
2. **MongoDB** - NoSQL, flexible schema, JSON-native
3. **SQLite** - Simple, file-based, no server needed

### Decision
Choose **PostgreSQL**

### Rationale
- **JSONB Support**: Can store structured extraction results as JSON
- **Relational**: Good for job history queries with indexes
- **ACID Compliance**: Reliable data integrity
- **Performance**: Excellent query performance with proper indexing
- **Familiarity**: Most developers know SQL
- **Future Features**: Supports complex queries for analytics

### Schema Example
```sql
CREATE TABLE extraction_jobs (
    id UUID PRIMARY KEY,
    url TEXT NOT NULL,
    prompt TEXT NOT NULL,
    result_data JSONB,  -- Flexible JSON storage
    status VARCHAR(20),
    created_at TIMESTAMP
);

CREATE INDEX idx_jobs_status ON extraction_jobs(status, created_at);
```

### Consequences
- Need to run PostgreSQL server (Docker makes this easy)
- JSONB is specific to PostgreSQL (vendor lock-in, but acceptable)

---

## Decision 6: Celery + Redis for Background Jobs
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Web scraping and LLM processing can take 30-60 seconds. Cannot block HTTP requests.

### Options Considered
1. **FastAPI BackgroundTasks** - Simple, but not persistent
2. **Celery + Redis** - Mature, distributed, persistent
3. **RQ (Redis Queue)** - Simpler than Celery, Python-only
4. **Dramatiq** - Modern alternative to Celery

### Decision
Use **Celery + Redis**

### Rationale
- **Maturity**: Battle-tested in production
- **Persistence**: Jobs survive worker restarts
- **Monitoring**: Flower for Celery monitoring
- **Distribution**: Can scale workers horizontally
- **Retry Logic**: Built-in retry and error handling
- **Ecosystem**: Large community and tooling

### Consequences
- More complex setup than simple background tasks
- Redis dependency
- Learning curve for Celery configuration

---

## Decision 7: Next.js over React SPA
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to choose frontend framework.

### Options Considered
1. **React SPA (Vite)** - Simple, client-side only
2. **Next.js** - React with SSR, routing, optimizations
3. **Remix** - Modern, web standards focus
4. **SvelteKit** - Fast, smaller bundle sizes

### Decision
Choose **Next.js 14 with App Router**

### Rationale
- **Performance**: Server components reduce client JavaScript
- **SEO**: Server-side rendering for landing page
- **Developer Experience**: Built-in routing, API routes, hot reload
- **Optimization**: Automatic code splitting, image optimization
- **Deployment**: Easy to deploy (Vercel, Docker)
- **Ecosystem**: Largest React framework ecosystem

### Consequences
- Larger framework than plain React
- Learning curve for App Router
- Server components vs client components decisions

---

## Decision 8: Token-Efficient HTML Processing
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Sending full HTML to LLM is expensive and inefficient. Large pages can be 100k+ tokens.

### Decision
**Pre-process HTML into compressed summary before sending to LLM**

### Rationale
- **Cost**: Token usage directly impacts API costs
- **Performance**: Smaller prompts = faster inference
- **Quality**: Focused context improves LLM accuracy
- **Limits**: Avoids hitting model context limits

### Implementation Strategy
1. Extract visible text only (ignore scripts, styles)
2. Identify structural elements (headings, lists, tables)
3. Find repeated patterns (product cards, article previews)
4. Extract key attributes (href, src, class, id for important elements)
5. Include page metadata (title, description, Open Graph tags)
6. Send compressed summary (typically 1-5k tokens instead of 50k+)

### Example
**Instead of**:
```html
<div class="product-card">
  <h3>Product Name</h3>
  <span class="price">$99</span>
  ...entire HTML...
</div>
```

**Send**:
```
Page Structure:
- Title: "Products | Example Store"
- Main content: 24 repeated ".product-card" elements
- Each card contains: h3 (product name), .price (number), .rating (1-5)
- Pattern detected: List of products with consistent structure
```

### Consequences
- Need to write HTML analysis logic
- Must balance compression vs information loss
- More complex than naive approach

---

## Decision 9: SSRF Protection Mandatory
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Users can provide arbitrary URLs. Without protection, attackers could scan internal networks.

### Decision
**Implement comprehensive SSRF protection before MVP launch**

### Rationale
- **Security**: Prevent internal network scanning
- **Compliance**: Standard security practice
- **Trust**: Users trust us not to attack their infrastructure
- **Liability**: Prevent abuse of our service

### Protection Mechanisms
1. Block private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
2. Block localhost (127.0.0.0/8)
3. Block link-local (169.254.0.0/16)
4. Block cloud metadata endpoints (169.254.169.254, metadata.google.internal)
5. Validate URLs after redirect resolution
6. Use DNS resolution to check final IP

### Consequences
- Cannot scrape localhost during development (use test domains)
- Slightly slower URL validation
- More complex validator code

---

## Decision 10: Cross-Model Continuity System
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Project may be developed by multiple AI coding agents across different sessions. Need continuity without conversation history.

### Decision
Implement **persistent documentation system** as single source of truth

### Rationale
- **Model Independence**: Works with any AI coding agent
- **Token Limits**: Handles context limit exhaustion gracefully
- **Handoff**: Enables smooth transitions between agents
- **Recovery**: Allows picking up after interruptions
- **Transparency**: Human developers can also follow along

### Implementation
- `AGENTS.md` - Main instruction file for all AI agents
- `docs/PROJECT_OVERVIEW.md` - Application purpose and goals
- `docs/ARCHITECTURE.md` - Technical architecture
- `docs/IMPLEMENTATION_PLAN.md` - All development phases with task checklists
- `docs/PROJECT_STATE.md` - Current status, what works, what doesn't
- `docs/DECISIONS.md` - This file
- `docs/CHANGELOG.md` - Development history
- `docs/HANDOFF.md` - Exact continuation point for next agent

### Consequences
- More documentation to maintain
- Discipline required to update files
- Worth it for long-term development flexibility

---

## Decision 11: MVP Scope Boundaries
**Date**: 2026-11-05
**Status**: ✅ Accepted

### Context
Need to define what's in scope for MVP vs future enhancements.

### Decision
**MVP includes single-page extraction only**

### In Scope
✅ Single-page data extraction
✅ Static and JS-rendered pages
✅ Natural language prompts
✅ JSON/CSV/Excel export
✅ Extraction history
✅ LLM provider fallback
✅ Basic error handling

### Out of Scope (Future)
🔮 Multi-page pagination
🔮 Infinite scroll handling
🔮 User authentication
🔮 API tokens for programmatic access
🔮 Scheduled/recurring extractions
🔮 Webhook notifications
🔮 Custom extraction rules UI
🔮 Chrome extension

### Rationale
- **Focus**: Build one thing really well
- **Timeline**: MVP should be achievable in reasonable time
- **Validation**: Test core value proposition first
- **Iteration**: Add features based on user feedback

### Consequences
- Must communicate limitations clearly to users
- Design architecture to support future features
- Prioritize core extraction quality

---

## Future Decisions

As development progresses, record new decisions here. Include:
- **Decision number and title**
- **Date**
- **Context** (why this decision was needed)
- **Options considered**
- **Decision made**
- **Rationale**
- **Consequences**

---

**Last Updated**: 2026-11-05 (Phase 1)
