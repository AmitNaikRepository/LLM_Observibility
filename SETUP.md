# Setup Guide

This guide will walk you through setting up the LLM Observability Dashboard step by step.

## Prerequisites Checklist

- [ ] Docker Desktop installed (or Docker + Docker Compose)
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Groq API key
- [ ] LangFuse account

## Step 1: Get API Keys

### Groq API Key

1. Go to https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Save it securely

### LangFuse Keys

1. Go to https://cloud.langfuse.com
2. Sign up for a free account
3. Create a new project
4. Go to Settings → API Keys
5. Copy both the Public Key and Secret Key

## Step 2: Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd LLM_Observibility

# Create environment file
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your preferred editor
```

Add your keys to `.env`:
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxx
```

## Step 3: Start Services

### Option A: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Wait for services to be healthy (about 30 seconds)
docker-compose ps
```

### Option B: Manual Setup

**Terminal 1 - Database:**
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu

# Create database
createdb llm_observability
psql llm_observability < database/schema.sql
```

**Terminal 2 - Redis:**
```bash
# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Ubuntu
```

**Terminal 3 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env with your keys

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Step 4: Verify Installation

### Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "metrics_service": "running"
}
```

### Check Frontend
Open browser to: http://localhost:5173

You should see the dashboard (empty at first).

## Step 5: Seed Test Data

```bash
# Install Python dependencies if not done already
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Run seeding script
python scripts/seed_data.py
```

Expected output:
```
Starting database seeding...
Connected to database
Generating 500 realistic metrics over 7 days...
Inserting 500 metrics...
Metrics inserted successfully
...
✅ Database seeding completed successfully!

Database Statistics:
  Total Metrics: 500
  Total Cost: $0.1234
  Success Rate: 90.00%
```

## Step 6: View Dashboard

1. Open http://localhost:5173 in your browser
2. You should see:
   - KPI cards with metrics
   - Charts populated with data
   - Live request feed showing recent calls

## Step 7: Make Your First Tracked Call

### Using curl:
```bash
curl -X POST http://localhost:8000/api/groq/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test_user" \
  -H "X-User-Role: admin" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "model": "llama-3.1-8b-instant",
    "user_id": "test_user",
    "user_role": "admin"
  }'
```

### Using Python:
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/groq/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "model": "llama-3.1-8b-instant",
        "user_id": "test_user",
        "user_role": "admin"
    }
)

print(response.json())
```

The request will appear in the Live Request Feed within 5 seconds!

## Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill the process
kill -9 <PID>
```

### Database Connection Failed

```bash
# Check if PostgreSQL is running
pg_isready

# If using Docker:
docker-compose exec postgres pg_isready

# Check credentials
psql -U postgres -d llm_observability -c "SELECT 1"
```

### Redis Connection Failed

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If using Docker:
docker-compose exec redis redis-cli ping
```

### Backend Errors

```bash
# Check backend logs
docker-compose logs backend

# Or if running manually:
# Check the terminal where uvicorn is running
```

### Frontend Not Loading

```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Or if running manually:
# Check the terminal where npm run dev is running

# Verify API URL in frontend/.env
echo $VITE_API_URL
```

### No Data Showing

1. Check if backend is running: `curl http://localhost:8000/health`
2. Seed test data: `python scripts/seed_data.py`
3. Check database: `psql llm_observability -c "SELECT COUNT(*) FROM llm_metrics"`
4. Check browser console for errors (F12)

## Next Steps

1. **Integrate with Your System**: Replace your Groq API calls with instrumented versions
2. **Configure Alerts**: Set up monitoring for errors and high costs
3. **Customize Pricing**: Update model costs in `backend/app/config.py`
4. **Scale Up**: Deploy to production with proper infrastructure
5. **Monitor LangFuse**: Check traces at https://cloud.langfuse.com

## Production Deployment

For production deployment:

1. Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
2. Use managed Redis (ElastiCache, Redis Cloud, etc.)
3. Deploy backend on container orchestration (Kubernetes, ECS, etc.)
4. Deploy frontend to CDN (Vercel, Netlify, Cloudflare Pages)
5. Set up proper secrets management (AWS Secrets Manager, Vault, etc.)
6. Configure monitoring and alerts
7. Set up database backups
8. Enable SSL/TLS
9. Configure rate limiting
10. Set up log aggregation

## Support

If you run into issues:
1. Check this troubleshooting guide
2. Review logs carefully
3. Check GitHub issues
4. Create a new issue with:
   - Your environment (OS, Docker version, etc.)
   - Error messages
   - Steps to reproduce
