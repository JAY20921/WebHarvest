# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│            (Next.js + TypeScript + Tailwind)               │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Landing Page │  │ Dashboard    │  │ History Page    │ │
│  └──────────────┘  └──────────────┘  └─────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ API Routes │  │ Services   │  │ Background Workers │  │
│  └────────────┘  └────────────┘  └────────────────────┘  │
└─────┬───────────────┬───────────────────┬─────────────────┘
      │               │                   │
      ▼               ▼                   ▼
┌──────────┐   ┌─────────────┐    ┌────────────┐
│PostgreSQL│   │ LLM Providers│    │   Redis    │
│ Database │   │ Groq/Gemini │    │   Queue    │
└──────────┘   └─────────────┘    └────────────┘
```

## Component Architecture

### 1. Frontend Layer

#### Technology Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **State Management**: React hooks + Context API
- **HTTP Client**: Fetch API / Axios

#### Key Pages

**Landing Page** (`/`)
- Hero section with value proposition
- URL input + prompt textarea
- Format selector (JSON/CSV/Excel)
- "Extract Data" CTA button
- Example prompts
- Feature highlights

**Dashboard** (`/dashboard`)
- Active extraction monitoring
- Real-time status updates
- Progress indicators
- Error display

**Results Page** (`/results/[jobId]`)
- Table view (sortable, filterable)
- JSON view (syntax highlighted)
- Raw data view
- Export buttons (JSON, CSV, Excel)
- Extraction metadata

**History Page** (`/history`)
- List of past extractions
- Filterable by date, URL, status
- Quick re-download
- Job details modal

#### Component Structure
```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (landing)
│   ├── dashboard/
│   ├── results/
│   └── history/
├── components/
│   ├── ui/ (shadcn components)
│   ├── ExtractionForm.tsx
│   ├── ResultsTable.tsx
│   ├── JsonViewer.tsx
│   ├── StatusBadge.tsx
│   └── HistoryCard.tsx
├── lib/
│   ├── api.ts (API client)
│   ├── utils.ts
│   └── types.ts
└── types/
    └── extraction.ts
```

### 2. Backend Layer

#### Technology Stack
- **Framework**: FastAPI (async)
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Task Queue**: Celery
- **Broker**: Redis

#### Directory Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   │
│   ├── api/
│   │   ├── deps.py          # Dependencies (DB session, etc.)
│   │   └── routes/
│   │       ├── extraction.py    # POST /api/extract, GET /api/extract/{id}
│   │       ├── history.py       # GET /api/history
│   │       ├── export.py        # GET /api/export/{id}
│   │       └── health.py        # GET /api/health
│   │
│   ├── core/
│   │   ├── config.py        # Settings (env vars)
│   │   ├── security.py      # SSRF protection, validation
│   │   ├── logging.py       # Structured logging setup
│   │   └── exceptions.py    # Custom exceptions
│   │
│   ├── services/
│   │   ├── llm_service.py       # High-level LLM orchestration
│   │   ├── scraping_service.py  # Scraping orchestration
│   │   ├── extraction_service.py # Extraction logic
│   │   ├── validation_service.py # Data validation
│   │   └── export_service.py    # Format conversion
│   │
│   ├── llm/
│   │   ├── base.py              # Abstract LLMProvider class
│   │   ├── provider_factory.py  # Factory pattern
│   │   ├── groq_provider.py     # Groq implementation
│   │   ├── gemini_provider.py   # Gemini implementation
│   │   ├── fallback_manager.py  # Automatic failover logic
│   │   └── prompts.py           # LLM prompt templates
│   │
│   ├── scrapers/
│   │   ├── base.py              # Abstract Scraper class
│   │   ├── http_scraper.py      # HTTPX-based scraper
│   │   ├── browser_scraper.py   # Playwright-based scraper
│   │   ├── html_parser.py       # BeautifulSoup wrapper
│   │   └── dom_analyzer.py      # Token-efficient HTML analysis
│   │
│   ├── models/
│   │   ├── database.py          # SQLAlchemy base
│   │   └── extraction.py        # ExtractionJob model
│   │
│   ├── schemas/
│   │   ├── extraction.py        # Request/response schemas
│   │   ├── llm.py               # LLM schema definitions
│   │   └── output.py            # Export schemas
│   │
│   ├── workers/
│   │   └── extraction_worker.py # Celery tasks
│   │
│   └── utils/
│       ├── url_validator.py     # URL validation + SSRF
│       ├── html_cleaner.py      # HTML sanitization
│       └── helpers.py           # Misc utilities
│
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_api/
│   ├── test_llm/
│   ├── test_scrapers/
│   └── test_integration/
│
├── requirements.txt
├── Dockerfile
└── alembic/                     # Database migrations
    └── versions/
```

### 3. API Endpoints

#### `POST /api/extract`
**Purpose**: Create new extraction job

**Request**:
```json
{
  "url": "https://example.com/products",
  "prompt": "Extract product names and prices",
  "output_format": "json"
}
```

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "pending",
  "created_at": "2026-11-05T10:30:00Z"
}
```

**Workflow**:
1. Validate URL (SSRF check)
2. Create database record
3. Enqueue Celery task
4. Return job ID immediately

#### `GET /api/extract/{job_id}`
**Purpose**: Get extraction status and results

**Response (in progress)**:
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": {
    "step": "extracting",
    "message": "Analyzing page structure..."
  }
}
```

**Response (completed)**:
```json
{
  "job_id": "uuid",
  "status": "completed",
  "url": "https://example.com/products",
  "prompt": "Extract product names and prices",
  "records_count": 24,
  "data": [
    {
      "name": "Product A",
      "price": 999
    }
  ],
  "completed_at": "2026-11-05T10:31:00Z"
}
```

#### `GET /api/history`
**Purpose**: List past extraction jobs

**Query Params**: `?limit=20&offset=0&status=completed`

**Response**:
```json
{
  "total": 100,
  "items": [
    {
      "job_id": "uuid",
      "url": "https://example.com",
      "prompt": "Extract...",
      "status": "completed",
      "records_count": 24,
      "created_at": "2026-11-05T10:30:00Z"
    }
  ]
}
```

#### `GET /api/export/{job_id}?format=csv`
**Purpose**: Export results in specific format

**Formats**: `json`, `csv`, `xlsx`

**Response**: File download with appropriate Content-Type

#### `GET /api/health`
**Purpose**: Health check

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "redis": "ok",
    "llm_primary": "ok",
    "llm_fallback": "ok"
  }
}
```

### 4. Database Schema

#### `extraction_jobs` Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| url | TEXT | Source website URL |
| prompt | TEXT | User's extraction instruction |
| output_format | VARCHAR(10) | json/csv/xlsx |
| status | VARCHAR(20) | pending/processing/completed/failed |
| extraction_schema | JSONB | LLM-generated schema |
| result_data | JSONB | Extracted data (JSON) |
| error_message | TEXT | Error details if failed |
| records_count | INTEGER | Number of extracted records |
| created_at | TIMESTAMP | Job creation time |
| started_at | TIMESTAMP | Processing start time |
| completed_at | TIMESTAMP | Completion time |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (status, created_at) - for history queries
- INDEX (created_at DESC) - for recent jobs

### 5. LLM Provider Architecture

#### Abstract Interface
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    async def generate_extraction_schema(
        self, 
        user_prompt: str, 
        page_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured extraction schema from prompt"""
        pass
    
    @abstractmethod
    async def identify_page_structure(
        self, 
        html_summary: str
    ) -> Dict[str, Any]:
        """Analyze page structure and identify patterns"""
        pass
```

#### Provider Implementations

**GroqProvider** (Primary)
- Uses Groq Cloud API
- Model: `mixtral-8x7b-32768` or `llama-3.1-70b-versatile`
- Fast inference (< 1s typically)
- JSON mode support

**GeminiProvider** (Fallback)
- Uses Google AI Studio API
- Model: `gemini-1.5-pro` or `gemini-1.5-flash`
- Generous rate limits
- Reliable fallback

#### Fallback Logic
```python
async def execute_with_fallback(operation):
    try:
        result = await groq_provider.execute(operation)
        return result
    except (RateLimitError, TimeoutError, ServiceUnavailable):
        logger.warning("Groq failed, falling back to Gemini")
        result = await gemini_provider.execute(operation)
        return result
    except Exception as e:
        logger.error(f"Both providers failed: {e}")
        raise ExtractionError("LLM service unavailable")
```

### 6. Scraping Engine Architecture

#### Scraper Selection Logic
```python
def select_scraper(url: str) -> Scraper:
    # Check if JavaScript rendering needed
    if requires_browser(url):
        return BrowserScraper(playwright)
    else:
        return HTTPScraper(httpx)
```

#### HTTP Scraper
- Uses `httpx` async client
- Handles: Static HTML pages
- Advantages: Fast, low resource usage
- Timeouts: 10s connection, 30s read

#### Browser Scraper
- Uses `Playwright` (Chromium)
- Handles: JavaScript-rendered pages, SPAs
- Advantages: Full page rendering
- Timeouts: 30s page load

#### HTML Analysis
**Token-Efficient Processing**:
1. Extract visible text
2. Identify structural elements (headings, lists, tables)
3. Find repeated patterns (product cards, articles)
4. Extract key attributes (links, images, prices)
5. Extract metadata (JSON-LD, OpenGraph)
6. **Compress**: Send summary to LLM, not full HTML

### 7. Extraction Workflow

```
User Request
    ↓
┌─────────────────────┐
│ 1. Validate URL     │
│    (SSRF check)     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 2. Create Job       │
│    (PostgreSQL)     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 3. Enqueue Task     │
│    (Celery + Redis) │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 4. Fetch Page       │
│    (HTTP/Playwright)│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 5. Parse HTML       │
│    (BeautifulSoup)  │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 6. LLM Analysis     │
│    (Schema Gen)     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 7. Extract Data     │
│    (Apply Schema)   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 8. Validate Results │
│    (Pydantic)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 9. Format Output    │
│    (JSON/CSV/Excel) │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 10. Store Results   │
│     (PostgreSQL)    │
└──────────┬──────────┘
           ↓
     Return to User
```

### 8. Security Architecture

#### SSRF Protection
**Block these targets**:
- `127.0.0.0/8` (localhost)
- `10.0.0.0/8` (private)
- `172.16.0.0/12` (private)
- `192.168.0.0/16` (private)
- `169.254.0.0/16` (link-local)
- `169.254.169.254` (cloud metadata)
- `metadata.google.internal`

**Implementation**:
```python
async def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    
    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        raise InvalidURLError()
    
    # Resolve DNS
    ip = await resolve_ip(parsed.hostname)
    
    # Check if IP is blacklisted
    if is_private_ip(ip):
        raise SSRFError()
    
    # Check redirects
    final_url = await follow_redirects(url)
    await validate_url(final_url)  # Recursive check
    
    return True
```

#### Resource Limits
- **Page Size**: 10 MB max
- **Extraction Time**: 5 minutes max
- **Request Timeout**: 30 seconds
- **LLM Timeout**: 45 seconds
- **Queue Size**: 1000 jobs max

#### Input Validation
- All API inputs: Pydantic validation
- URLs: Custom validator with SSRF check
- LLM outputs: JSON schema validation
- Extracted data: Type checking

### 9. Environment Configuration

**Backend (.env)**:
```env
# LLM Configuration
LLM_PRIMARY_PROVIDER=groq
LLM_FALLBACK_PROVIDER=gemini
LLM_FALLBACK_ENABLED=true
GROQ_API_KEY=your_key_here
GROQ_MODEL=mixtral-8x7b-32768
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/scraper_db

# Redis
REDIS_URL=redis://redis:6379/0

# API
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
SECRET_KEY=random_secret_key_here

# Timeouts
LLM_TIMEOUT_SECONDS=45
SCRAPING_TIMEOUT_SECONDS=30
EXTRACTION_TIMEOUT_MINUTES=5

# Limits
MAX_PAGE_SIZE_MB=10
MAX_CONCURRENT_JOBS=10
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 10. Deployment Architecture (Docker Compose)

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
  
  postgres:
    image: postgres:15
    volumes: [postgres_data:/var/lib/postgresql/data]
  
  redis:
    image: redis:7-alpine
  
  celery_worker:
    build: ./backend
    command: celery -A app.workers.extraction_worker worker
    depends_on: [postgres, redis]
```

### 11. Data Flow Example

**Scenario**: Extract product information

**Input**:
```json
{
  "url": "https://shop.example.com/laptops",
  "prompt": "Extract laptop name, price, RAM, and storage",
  "output_format": "json"
}
```

**Step-by-Step**:

1. **API receives request**
   - Validates URL (passes SSRF check)
   - Creates job record (status: pending)
   - Returns job_id to frontend

2. **Celery worker picks up job**
   - Updates status to "processing"
   - Selects scraper (Playwright needed for this site)

3. **Browser scraper fetches page**
   - Renders JavaScript
   - Waits for network idle
   - Captures final HTML

4. **HTML parser analyzes page**
   - Identifies repeated product cards
   - Extracts text, prices, attributes
   - Creates compressed summary

5. **LLM generates schema**
   - Prompt: "User wants: laptop name, price, RAM, storage"
   - Page summary: "Products in .product-card divs..."
   - Output schema:
     ```json
     {
       "fields": {
         "name": "string",
         "price": "number",
         "ram": "string",
         "storage": "string"
       },
       "selectors": {
         "container": ".product-card",
         "name": "h3.product-title",
         "price": ".price-value"
       }
     }
     ```

6. **Extraction engine applies schema**
   - Finds all `.product-card` elements
   - Extracts fields using selectors
   - Normalizes data (e.g., "₹1,499" → 1499)

7. **Validation service checks results**
   - Validates against Pydantic model
   - Flags missing/invalid fields
   - Reports extraction quality

8. **Export service formats data**
   - Converts to JSON
   - Stores in database

9. **Frontend polls and displays**
   - Shows table with 15 products
   - Allows download as JSON/CSV/Excel

---

**Next Document**: See `IMPLEMENTATION_PLAN.md` for development phases.
