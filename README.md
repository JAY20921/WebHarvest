# Intelligent Scraper

**AI-Powered Natural Language Website Data Extraction Platform**

Extract structured data from any website using plain English instructions. No CSS selectors, no XPath, no scraping knowledge required.

## 🎯 What Is This?

Intelligent Scraper lets you describe what data you want in natural language, and AI figures out how to extract it.

**Example**:
```
URL: https://example.com/products
Prompt: "Extract all product names, prices, ratings, and review counts"
Output: Clean JSON/CSV/Excel with the actual data
```

## ✨ Features

- 🤖 **Natural Language Instructions** - Describe what you need in plain English
- 🧠 **AI-Powered Understanding** - LLM interprets your intent and generates extraction schemas
- 🌐 **Universal Compatibility** - Handles both static HTML and JavaScript-rendered pages
- 📊 **Multiple Export Formats** - JSON, CSV, and Excel
- 🔄 **Automatic LLM Fallback** - Groq (primary) → Gemini (fallback) for reliability
- 📜 **Extraction History** - Track and re-download previous extractions
- 🔒 **Security First** - SSRF protection, URL validation, resource limits

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** (strict mode)
- **Tailwind CSS** + shadcn/ui components
- **Lucide React** icons

### Backend
- **FastAPI** (async Python 3.11+)
- **PostgreSQL** with SQLAlchemy ORM
- **Celery** + Redis for background jobs
- **Playwright** + HTTPX for web scraping
- **BeautifulSoup** for HTML parsing

### AI/LLM
- **Groq API** (primary provider)
- **Google Gemini API** (fallback provider)
- Provider-agnostic abstraction layer

### DevOps
- **Docker** + Docker Compose
- **Git** version control

## 📋 Prerequisites

- Docker and Docker Compose
- Groq API key ([Get here](https://console.groq.com/))
- Google Gemini API key ([Get here](https://aistudio.google.com/app/apikey))

**Optional for local development**:
- Node.js 18+
- Python 3.11+

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd intelligent-scrapper
```

### 2. Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start All Services
```bash
docker-compose up -d
```

This will start:
- **Frontend** (http://localhost:3000)
- **Backend API** (http://localhost:8000)
- **API Docs** (http://localhost:8000/docs)
- **PostgreSQL** database
- **Redis** message broker
- **Celery** background worker

### 4. Check Health
```bash
curl http://localhost:8000/api/health
```

### 5. Open the Application
Navigate to http://localhost:3000

## 🧪 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
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

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### `POST /api/extract`
Create a new extraction job
```json
{
  "url": "https://example.com/products",
  "prompt": "Extract product names and prices",
  "output_format": "json"
}
```

#### `GET /api/extract/{job_id}`
Get extraction status and results

#### `GET /api/history`
List previous extraction jobs

#### `GET /api/export/{job_id}?format=csv`
Export results in specific format

#### `GET /api/health`
Health check

## 🗂️ Project Structure

```
intelligent-scrapper/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, logging
│   │   ├── services/       # Business logic
│   │   ├── llm/            # LLM provider abstraction
│   │   ├── scrapers/       # Web scraping engines
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── workers/        # Celery workers
│   │   └── utils/          # Utilities
│   └── tests/
│
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── public/
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
├── AGENTS.md              # AI agent instructions
└── README.md              # This file
```

## 🔐 Security

### SSRF Protection
The application blocks requests to:
- Localhost (127.0.0.0/8)
- Private networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Link-local addresses (169.254.0.0/16)
- Cloud metadata endpoints

### Resource Limits
- Maximum page size: 10 MB
- Extraction timeout: 5 minutes
- Request timeout: 30 seconds
- LLM timeout: 45 seconds

### Data Validation
- All user inputs validated (Pydantic)
- All LLM outputs validated (JSON schema)
- All extracted data type-checked
- External content treated as untrusted

## 🎯 MVP Scope

### Included
✅ Single-page extraction  
✅ Static and JavaScript-rendered pages  
✅ Natural language instructions  
✅ JSON/CSV/Excel export  
✅ Extraction history  
✅ Automatic LLM fallback  

### Future Enhancements
🔮 Multi-page pagination  
🔮 Infinite scroll handling  
🔮 User authentication  
🔮 API access tokens  
🔮 Scheduled extractions  
🔮 Webhook notifications  

## 🤝 Contributing

This project uses a documentation-based continuity system designed for multi-agent development. If you're an AI coding agent:

1. Read `AGENTS.md` first
2. Review all documentation in `docs/` folder
3. Check `docs/PROJECT_STATE.md` for current status
4. Follow the implementation plan in `docs/IMPLEMENTATION_PLAN.md`

## 📝 License

[License information to be added]

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and modern AI APIs
- Powered by Groq and Google Gemini
- UI components from shadcn/ui

---

**Version**: 0.1.0-dev  
**Status**: MVP Development in Progress  
**Last Updated**: 2026-11-05
