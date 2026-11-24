# ☁️ Cloud Deployment Guide

This guide walks you through deploying the Intelligent Scraper using cloud-hosted databases instead of local Docker containers.

## ✅ Prerequisites

1. **Cloud PostgreSQL Database** (choose one):
   - [Neon](https://neon.tech) - Serverless Postgres (Free tier available)
   - [Supabase](https://supabase.com) - Full Postgres with extras (Free tier)
   - [Railway](https://railway.app) - Simple deployment (Free tier)
   - [AWS RDS](https://aws.amazon.com/rds/) - Production-grade
   - [Heroku Postgres](https://www.heroku.com/postgres) - Easy setup

2. **Cloud Redis** (choose one):
   - [Upstash](https://upstash.com) - Serverless Redis (Free tier)
   - [Redis Cloud](https://redis.com/try-free/) - Managed Redis (Free tier)
   - [Railway](https://railway.app) - Simple Redis deployment

3. **API Keys** (already have these):
   - Groq API Key
   - Google Gemini API Key

---

## 📝 Step 1: Set Up Cloud PostgreSQL

### Option A: Neon (Recommended for Development)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project
3. Copy the connection string (looks like):
   ```
   postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
   ```
4. Paste it into your `.env` file as `DATABASE_URL`

### Option B: Supabase

1. Go to [supabase.com](https://supabase.com) and create a project
2. Go to Settings → Database
3. Copy the "Connection string" (URI format)
4. Update your `.env` file with this URL

### Option C: Railway

1. Go to [railway.app](https://railway.app) and create a new project
2. Add PostgreSQL from the marketplace
3. Copy the connection string from the "Connect" tab
4. Update your `.env` file

---

## 📝 Step 2: Set Up Cloud Redis

### Option A: Upstash (Recommended)

1. Go to [upstash.com](https://upstash.com) and sign up
2. Create a new Redis database
3. Copy the connection string (looks like):
   ```
   rediss://:password@us1-xxx.upstash.io:6379
   ```
4. Update your `.env`:
   ```env
   REDIS_URL=rediss://:password@us1-xxx.upstash.io:6379
   CELERY_BROKER_URL=rediss://:password@us1-xxx.upstash.io:6379
   CELERY_RESULT_BACKEND=rediss://:password@us1-xxx.upstash.io:6379
   ```

### Option B: Redis Cloud

1. Go to [redis.com/try-free](https://redis.com/try-free/) and sign up
2. Create a new subscription (free tier)
3. Create a database
4. Copy the connection string
5. Update your `.env` file

---

## 📝 Step 3: Update Environment Variables

Edit `d:\WEB\Intelligent Scrapper\.env`:

```env
# Cloud PostgreSQL (replace with your actual connection string)
DATABASE_URL=postgresql://user:pass@your-db-host.com:5432/dbname?sslmode=require

# Cloud Redis (replace with your actual connection string)
REDIS_URL=rediss://:password@your-redis-host.com:6379
CELERY_BROKER_URL=rediss://:password@your-redis-host.com:6379
CELERY_RESULT_BACKEND=rediss://:password@your-redis-host.com:6379

# API Keys (keep your real keys only in .env)
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 📝 Step 4: Database Tables

No migration step is needed. The backend creates its tables automatically on startup
(`init_db()` in `backend/app/models/database.py`). The connection check below also creates them.

Cloud URLs work as copied from the provider dashboard. The backend converts them for asyncpg
automatically (`sslmode=require` → SSL on, `channel_binding` stripped, `postgres://` accepted,
PgBouncer/pooler hosts get the prepared-statement cache disabled).

---

## 🚀 Step 5: Run Without Docker (Windows)

One-time setup:

```powershell
cd "d:\WEB\Intelligent Scrapper\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium

cd ..\frontend
npm install
```

Check that every cloud service is reachable (never prints secrets):

```powershell
cd "d:\WEB\Intelligent Scrapper\backend"
.\venv\Scripts\python -m scripts.check_connections
# Summary: postgres=OK, redis=OK, llm_keys=OK
```

Then start the app in **three terminals**:

```powershell
# Terminal 1 - API
cd "d:\WEB\Intelligent Scrapper\backend"; .\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 - background worker (uses the "solo" pool automatically on Windows)
cd "d:\WEB\Intelligent Scrapper\backend"; .\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 - frontend
cd "d:\WEB\Intelligent Scrapper\frontend"
npm run dev
```

The backend reads the `.env` in the repo root even when started from `backend/`.

> Docker alternative: `docker-compose -f docker-compose.cloud.yml up --build -d` runs the
> same three processes in containers against the same cloud services.

---

## ✅ Step 6: Verify Everything Works

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
# status: healthy, database: ok

start http://localhost:3000
```

> **Upstash note:** Celery polls Redis constantly, even when idle, which uses up the
> free-tier command quota. Stop the worker when you are not using the app.

---

## 📊 Testing Your First Extraction

1. Go to **http://localhost:3000**
2. Enter URL: `https://news.ycombinator.com`
3. Prompt: `"Extract all article titles and links"`
4. Format: **JSON**
5. Click **"Extract Data"**
6. Wait 10-20 seconds
7. View results!

---

## 🛠️ Troubleshooting

### "Database connection failed"
- Check your `DATABASE_URL` is correct
- Ensure SSL mode is enabled if required (`?sslmode=require`)
- Verify firewall allows connections

### "Redis connection failed"  
- Check `REDIS_URL` format (use `rediss://` for SSL)
- Verify credentials are correct
- Check if IP whitelisting is required

### "Worker not processing jobs"
- Check the worker terminal output (or `docker logs intelligent-scraper-worker` if using Docker)
- Verify Redis connection works
- Ensure `CELERY_BROKER_URL` matches `REDIS_URL`

---

## 🎯 Production Deployment Options

Once working locally, you can deploy to:

1. **Backend + Worker**:
   - [Railway](https://railway.app) - One-click deploy
   - [Render](https://render.com) - Free tier available
   - [Fly.io](https://fly.io) - Edge deployment
   - AWS ECS / Google Cloud Run / Azure Container Apps

2. **Frontend**:
   - [Vercel](https://vercel.com) - Built for Next.js (Free tier)
   - [Netlify](https://netlify.com) - Easy deployments
   - [Railway](https://railway.app) - Same as backend

---

## 📝 Cost Estimates (Free Tiers)

| Service | Free Tier | Enough For |
|---------|-----------|------------|
| **Neon Postgres** | 512 MB storage, 3 GB data transfer | ~10K extractions |
| **Upstash Redis** | 10K commands/day | ~1K extractions/day |
| **Groq API** | Rate limited, free tier | Testing/development |
| **Gemini API** | 60 requests/min free | Fallback provider |

**Total monthly cost with free tiers: $0** ✅

---

## 🔄 Switching Back to Local

If you want to go back to local Docker databases:

```powershell
docker-compose -f docker-compose.yml up --build -d
```

This runs the full stack locally (postgres + redis + backend + worker + frontend).

---

**Questions?** Check the logs:
```powershell
docker logs intelligent-scraper-backend
docker logs intelligent-scraper-worker
```
