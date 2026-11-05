# AI Coding Agent Instructions

## Project Overview

This is an **AI-Powered Natural Language Website Data Extraction Platform**. Users describe what data they want in plain English, provide a URL, and the system intelligently extracts and returns structured data (JSON/CSV/Excel).

**Core Value Proposition**: No CSS selectors, no XPath, no scraping knowledge required. Just describe what you need.

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Queue**: Celery + Redis
- **Validation**: Pydantic v2

### Scraping
- **Browser Automation**: Playwright (for JS-rendered pages)
- **HTTP Client**: HTTPX (for static pages)
- **HTML Parser**: BeautifulSoup4

### LLM/AI
- **Primary Provider**: Groq API
- **Fallback Provider**: Google Gemini API
- **Architecture**: Provider-agnostic abstraction layer with automatic failover

### DevOps
- **Containerization**: Docker + Docker Compose
- **Version Control**: Git

## Project Structure

```
intelligent-scrapper/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application entry
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, logging
│   │   ├── services/       # Business logic services
│   │   ├── llm/            # LLM provider abstraction
│   │   ├── scrapers/       # Web scraping engines
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── workers/        # Celery workers
│   │   └── utils/          # Helper functions
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   ├── public/            # Static assets
│   ├── package.json
│   └── Dockerfile
│
├── docs/                   # Project documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── PROJECT_STATE.md
│   ├── DECISIONS.md
│   ├── CHANGELOG.md
│   └── HANDOFF.md
│
├── docker-compose.yml      # Container orchestration
├── .env.example           # Environment template
├── AGENTS.md              # This file
└── README.md              # Setup instructions
```

## Important Coding Conventions

### Python Backend
- **Async by default**: Use `async def` for I/O operations
- **Type hints**: Always use Python type annotations
- **Error handling**: Use custom exceptions, never silent failures
- **Logging**: Use structured logging (JSON format)
- **Validation**: Pydantic for all API inputs/outputs

### TypeScript Frontend
- **Strict mode**: Enable strict TypeScript checking
- **Functional components**: Use React hooks, no class components
- **Server components**: Prefer Next.js server components where appropriate
- **Type safety**: No `any` types without explicit justification

### Security Rules (MANDATORY)
1. **SSRF Protection**: Block localhost, 127.0.0.0/8, 169.254.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, cloud metadata endpoints
2. **URL Validation**: Validate before AND after redirects
3. **Secrets Management**: Never commit .env files, API keys, or credentials
4. **Input Sanitization**: Treat all external data (web pages, user input) as untrusted
5. **LLM Output Validation**: Always validate LLM responses with Pydantic
6. **Resource Limits**: Enforce timeouts, page size limits, extraction job duration limits

## How to Run the Project

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your API keys to .env
#    - GROQ_API_KEY
#    - GEMINI_API_KEY

# 3. Start all services
docker-compose up -d

# 4. Access the application
#    Frontend: http://localhost:3000
#    Backend API: http://localhost:8000
#    API Docs: http://localhost:8000/docs
```

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Critical Architecture Principles

### 1. Separation of Concerns
- **LLM**: Understands user intent, generates extraction schemas, identifies strategies
- **Scraper**: Fetches actual webpage content and retrieves real values
- **Validator**: Validates and structures extracted data

**NEVER use the LLM to fabricate or invent data values.** The LLM is for understanding and strategy, not for creating fake data.

### 2. Provider-Agnostic LLM Layer
All LLM providers implement a common interface:
```python
class LLMProvider(ABC):
    async def generate_extraction_schema(...)
    async def identify_page_structure(...)
    async def map_fields_to_elements(...)
```

Fallback logic: Groq → (on rate limit/timeout) → Gemini

### 3. Token-Efficient HTML Processing
Do NOT send entire HTML to LLM. Extract:
- Visible text content
- Structural elements (headings, lists, tables)
- Repeated patterns (product cards, article previews)
- Key attributes (href, src, class, id)
- Metadata (Open Graph, JSON-LD)

### 4. Defensive Validation
- Validate at API boundaries (Pydantic)
- Validate LLM outputs (JSON schema)
- Validate extracted data (type checking)
- Never trust external webpage content

## Documentation Requirements

### Before Modifying Code
**ALWAYS read these files first:**
1. `AGENTS.md` (this file)
2. `docs/PROJECT_OVERVIEW.md`
3. `docs/ARCHITECTURE.md`
4. `docs/PROJECT_STATE.md`
5. `docs/HANDOFF.md`

### While Coding
Update these files after completing significant work:
- `PROJECT_STATE.md` - Current status, what works, what doesn't
- `IMPLEMENTATION_PLAN.md` - Mark tasks as completed
- `CHANGELOG.md` - Record meaningful changes

### Before Stopping
Update `HANDOFF.md` with:
- What was completed
- What was started but unfinished
- Exact next steps
- Known issues
- Commands to verify state

## Cross-Model Handoff Protocol

This project is designed to be developed by multiple AI coding agents across different sessions. Git repository + persistent documentation = single source of truth.

### When Taking Over Development
1. Read all documentation in `docs/` folder
2. Run `git status` to see current state
3. Verify documented features by running tests
4. Check `HANDOFF.md` for the exact stopping point
5. **Do NOT rewrite working modules**
6. Continue from the next incomplete task

### When Stopping Development
1. Finish current atomic task if possible
2. Commit working code (never leave broken state)
3. Update all documentation files
4. Generate handoff prompt in `HANDOFF.md`
5. Mark incomplete work clearly

### Handoff Verification
The handoff is successful when a fresh AI agent can:
- Understand the project from documentation alone
- Identify the exact stopping point
- Run existing tests successfully
- Continue implementation without starting over

## Testing Strategy

### Test Coverage Requirements
- URL validation and SSRF protection
- LLM provider fallback behavior
- Schema generation and validation
- Extraction accuracy
- Export formats (JSON/CSV/Excel)
- API endpoints
- Error handling

### Mock LLM Responses
Use mocked LLM responses in tests to avoid API costs. Simulate:
- Successful schema generation
- Rate limit errors (test fallback)
- Timeout errors (test retry logic)
- Malformed responses (test validation)

## Known Limitations (MVP Scope)

**In Scope:**
- Single-page extraction
- Publicly accessible websites
- Static and JavaScript-rendered pages
- Basic authentication (future)

**Out of Scope (for now):**
- CAPTCHA bypass
- Multi-page pagination (future enhancement)
- Infinite scroll handling (future enhancement)
- Login/authentication flows
- Rate-limited sites requiring complex session management

## Emergency Procedures

### If Tests Fail
1. Read error messages carefully
2. Check recent code changes
3. Verify environment variables
4. Check Docker container logs
5. Rollback to last working commit if needed

### If LLM Providers Fail
1. Check API keys in `.env`
2. Verify network connectivity
3. Check provider status pages
4. Ensure fallback provider is configured
5. Review logs for specific error codes

### If Context Limit Reached
1. Save all work immediately
2. Run tests to verify state
3. Update PROJECT_STATE.md
4. Update HANDOFF.md with current position
5. Generate handoff prompt for next agent

## Contact Information

**Project Repository**: Local Git repository
**Documentation**: All in `docs/` directory
**State Tracking**: `PROJECT_STATE.md` and `HANDOFF.md`

---

## Quick Reference Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop everything
docker-compose down

# Run backend tests
docker-compose exec backend pytest

# Access database
docker-compose exec postgres psql -U scraper -d scraper_db

# Rebuild after code changes
docker-compose up -d --build

# Check service health
curl http://localhost:8000/api/health
```

---

**Remember**: This project prioritizes a genuinely working MVP with intelligent natural-language extraction, not an overcomplicated system with many unfinished features. Build incrementally, test continuously, and document thoroughly.
