# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Cloud databases + health check fixes (2026-11-23)

**Fixed**
- Cloud Postgres URLs (Neon/Supabase/Railway) now work with asyncpg: `sslmode`/`channel_binding` converted or stripped, `postgres://` accepted, pooler hosts get `statement_cache_size=0` (`app/models/database.py`)
- Celery works with TLS Redis (`rediss://`, Upstash/Redis Cloud); uses `solo` pool on Windows (`app/workers/celery_app.py`)
- Worker disposes the DB engine after each task (avoids "attached to a different loop" on the 2nd job)
- `.env` in repo root is found when the backend is started from `backend/`
- Retired LLM models replaced: Groq `openai/gpt-oss-120b`, Gemini `gemini-3.5-flash-lite`
- Extraction: string fields on links returned the href instead of text; truncated link text falls back to `title`; supports LLM-emitted `::attr(x)` / `::text` selectors
- Number parsing: `"1,299"` was parsed as `1.299`
- Jobs could not be queued: unpinned kombu 5.7 requires redis-py>=6.1; pinned `kombu==5.4.2`
- Frontend build failed: `llm_provider_used` missing from `ExtractionJob` type

**Added**
- `backend/scripts/check_connections.py`: checks Postgres, Redis and LLM keys
- `tests/test_extraction_field_values.py` (39 backend tests total, all passing)
- No-Docker run instructions in `CLOUD_SETUP.md`

### Phase 1: Project Foundation (2026-11-05) ✅ COMPLETE

#### Added
- ✅ Initialized Git repository
- ✅ Created `.gitignore` with Python, Node, Docker, IDE exclusions
- ✅ Created `AGENTS.md` - comprehensive instructions for AI coding agents
- ✅ Created `docs/PROJECT_OVERVIEW.md` - application purpose, features, use cases
- ✅ Created `docs/ARCHITECTURE.md` - system architecture, components, data flow
- ✅ Created `docs/IMPLEMENTATION_PLAN.md` - all 16 development phases with tasks
- ✅ Created `docs/PROJECT_STATE.md` - current status tracking
- ✅ Created `docs/DECISIONS.md` - technical decision records with rationale
- ✅ Created `docs/CHANGELOG.md` - this file
- ✅ Created `docs/HANDOFF.md` - cross-model continuity instructions
- ✅ Created `.env.example` - complete environment variable template
- ✅ Created `docker-compose.yml` - all services configured
- ✅ Created `README.md` - comprehensive setup instructions
- ✅ Created backend directory structure with FastAPI skeleton
- ✅ Created `backend/requirements.txt` - all Python dependencies
- ✅ Created `backend/Dockerfile` - backend containerization
- ✅ Created `backend/app/main.py` - FastAPI application entry point
- ✅ Created `backend/app/core/config.py` - environment configuration
- ✅ Created frontend directory structure with Next.js App Router
- ✅ Created `frontend/package.json` - all Node.js dependencies
- ✅ Created `frontend/Dockerfile` - frontend containerization
- ✅ Created `frontend/src/app/layout.tsx` - root layout
- ✅ Created `frontend/src/app/page.tsx` - landing page skeleton
- ✅ Created `frontend/src/types/extraction.ts` - TypeScript type definitions
- ✅ Created `frontend/src/lib/api.ts` - API client structure
- ✅ Configured Tailwind CSS and shadcn/ui foundation

#### Changed
- None yet (initial setup)

#### Deprecated
- None

#### Removed
- None

#### Fixed
- None

#### Security
- SSRF protection requirements documented in architecture and decisions

---

## Development Guidelines

### When to Update This File
Update this changelog:
- After completing each development phase
- After fixing significant bugs
- After making architectural changes
- After adding/removing major features
- Before creating handoff documentation

### What to Record
**Do Record**:
- New features or modules
- API changes
- Bug fixes
- Security improvements
- Breaking changes
- Dependency updates

**Don't Record**:
- Minor code refactoring
- Documentation typo fixes
- Internal variable renames
- Trivial changes

### Format
Use these categories:
- **Added**: New features, files, or functionality
- **Changed**: Changes to existing functionality
- **Deprecated**: Features marked for removal
- **Removed**: Removed features or files
- **Fixed**: Bug fixes
- **Security**: Security improvements or fixes

---

## Upcoming Changes

### Phase 2: Backend Core Setup (Planned)
- [ ] FastAPI application setup
- [ ] PostgreSQL database configuration
- [ ] SQLAlchemy models
- [ ] Alembic migrations
- [ ] Health check endpoint
- [ ] Docker configuration

### Phase 3: URL Validation & SSRF Protection (Planned)
- [ ] URL validator with SSRF protection
- [ ] Private IP blocking
- [ ] Cloud metadata endpoint blocking
- [ ] Security tests

### Phase 4: Scraping Engine (Planned)
- [ ] HTTP scraper (HTTPX)
- [ ] Browser scraper (Playwright)
- [ ] HTML parser (BeautifulSoup)
- [ ] DOM analyzer

### Phase 5: LLM Integration (Planned)
- [ ] Provider abstraction layer
- [ ] Groq provider
- [ ] Gemini provider
- [ ] Automatic fallback manager

---

## Version History

**Current Version**: 0.1.0-dev (In Development)

### Version 0.1.0-dev (2026-11-05)
- Initial project setup
- Documentation system established
- Cross-model continuity framework created

---

**Note**: This project is currently in MVP development. Version 1.0.0 will be assigned when the MVP is complete and functional.
