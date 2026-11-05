# Project Overview

## Application Name
**Intelligent Scraper** - AI-Powered Natural Language Website Data Extraction Platform

## Purpose
Transform any website into structured data using plain English instructions. Users describe what they need, and AI handles the extraction complexity.

## Core Problem Solved
Traditional web scraping requires:
- HTML/CSS knowledge
- Writing selectors and XPath
- Understanding page structure
- Handling edge cases manually
- Maintaining brittle scraping scripts

**Our Solution**: Just describe what you want in natural language. AI figures out how to extract it.

## Target Users
- Business analysts needing market data
- Researchers collecting information
- Data scientists gathering training datasets
- Non-technical users requiring web data
- Developers wanting to prototype data collection quickly

## Key Features

### 1. Natural Language Extraction
```
User Input: "Extract all product names, prices, and ratings"
System Output: Structured JSON/CSV/Excel with actual data
```

### 2. Intelligent Understanding
- LLM interprets user intent
- Identifies relevant page elements
- Generates extraction schemas
- Maps fields to DOM elements
- Validates extracted data

### 3. Universal Compatibility
- Static HTML pages
- JavaScript-rendered content (Playwright)
- Dynamic websites
- Various page structures

### 4. Multiple Export Formats
- JSON (developer-friendly)
- CSV (spreadsheet import)
- Excel/XLSX (business-friendly)

### 5. Extraction History
- Track previous extractions
- Re-download results
- Learn from past queries

### 6. Resilient LLM Architecture
- Primary provider: Groq (fast, cost-effective)
- Automatic fallback: Google Gemini
- Handles rate limits gracefully
- No manual intervention needed

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js + TypeScript | Modern React-based UI |
| UI Components | shadcn/ui + Tailwind | Beautiful, accessible design |
| Backend | FastAPI + Python | High-performance async API |
| Database | PostgreSQL | Reliable data persistence |
| Queue | Celery + Redis | Background job processing |
| Scraping | Playwright + HTTPX | Universal web content access |
| AI/LLM | Groq + Gemini | Intelligent extraction logic |
| Deployment | Docker Compose | Easy local development |

## User Workflow

```
1. User visits website
   ↓
2. Enters target URL (e.g., e-commerce product page)
   ↓
3. Writes instruction: "Get product name, price, rating, and reviews"
   ↓
4. Selects output format (JSON/CSV/Excel)
   ↓
5. Clicks "Extract Data"
   ↓
6. System processes:
   - Validates URL
   - Fetches webpage
   - Sends to LLM for analysis
   - Extracts actual data
   - Validates results
   ↓
7. User sees results in table view
   ↓
8. Downloads in chosen format
```

## System Workflow

```
Frontend Request
       ↓
   FastAPI validates and creates job
       ↓
   Celery worker picks up job
       ↓
   Scraper fetches webpage (HTTPX or Playwright)
       ↓
   LLM analyzes request + page structure
       ↓
   LLM generates extraction schema
       ↓
   Extraction engine applies schema to DOM
       ↓
   Pydantic validates extracted data
       ↓
   Export service formats results
       ↓
   Results stored in PostgreSQL
       ↓
   Frontend displays and allows download
```

## Security & Safety

### SSRF Protection
Block access to:
- Localhost (127.0.0.0/8)
- Private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Link-local addresses (169.254.0.0/16)
- Cloud metadata endpoints (169.254.169.254, etc.)

### Resource Limits
- Page size limits (prevent memory exhaustion)
- Extraction timeouts (prevent infinite loops)
- Rate limiting (prevent abuse)
- Request timeouts (prevent hanging)

### Data Validation
- All user inputs validated (Pydantic)
- All LLM outputs validated (JSON schema)
- All extracted data type-checked
- External content treated as untrusted

## MVP Scope

### Included in MVP
✅ Single-page extraction
✅ Static and JS-rendered pages
✅ Natural language instructions
✅ JSON/CSV/Excel export
✅ Extraction history
✅ Groq + Gemini providers
✅ Automatic LLM fallback
✅ Docker deployment
✅ Basic error handling

### Future Enhancements
🔮 Multi-page pagination
🔮 Infinite scroll handling
🔮 User authentication
🔮 API access tokens
🔮 Scheduled extractions
🔮 Webhook notifications
🔮 Custom extraction rules
🔮 Data transformation pipelines
🔮 Chrome extension

## Success Criteria

The MVP is successful when:
1. ✅ User can start the application locally
2. ✅ User can enter any public URL
3. ✅ User can describe extraction in plain English
4. ✅ System correctly extracts requested data
5. ✅ User can download results in all formats
6. ✅ LLM fallback works automatically
7. ✅ Extraction history is accessible
8. ✅ AI coding agents can continue development using documentation

## Competitive Advantages

| Feature | Traditional Scrapers | Intelligent Scraper |
|---------|---------------------|---------------------|
| Technical Knowledge | CSS/XPath required | Plain English |
| Setup Time | Hours to days | Seconds |
| Maintenance | Breaks on page changes | AI adapts |
| User Experience | Developer tools | Consumer-friendly UI |
| Flexibility | Fixed selectors | Natural language |

## Example Use Cases

### E-Commerce Research
```
URL: https://store.example.com/phones
Prompt: "Extract phone model, price, rating, and number of reviews"
Use: Competitive pricing analysis
```

### Job Hunting
```
URL: https://careers.example.com/openings
Prompt: "Get job title, location, salary range, and application deadline"
Use: Track opportunities across companies
```

### Content Aggregation
```
URL: https://blog.example.com
Prompt: "Extract article title, author, publish date, and summary"
Use: Build content curation database
```

### Real Estate
```
URL: https://listings.example.com
Prompt: "Get property address, price, bedrooms, bathrooms, and square footage"
Use: Market analysis
```

## Project Goals

### Technical Goals
- 🎯 Build genuinely working extraction pipeline
- 🎯 Implement intelligent LLM-based understanding
- 🎯 Ensure reliable provider fallback
- 🎯 Create maintainable, documented codebase
- 🎯 Enable cross-model development continuity

### User Experience Goals
- 🎯 Make web scraping accessible to non-developers
- 🎯 Provide instant feedback and clear errors
- 🎯 Ensure data accuracy and reliability
- 🎯 Deliver professional, intuitive interface

### Business Goals
- 🎯 Validate product-market fit
- 🎯 Demonstrate AI-powered automation value
- 🎯 Create foundation for SaaS product
- 🎯 Build extensible architecture for future features

---

**Next Steps**: See `IMPLEMENTATION_PLAN.md` for detailed development phases.
