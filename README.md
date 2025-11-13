# LLM Observability Dashboard

A comprehensive production-grade observability platform for Large Language Model (LLM) systems with real-time monitoring, cost tracking, and performance analytics.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-green)
![License](https://img.shields.io/badge/License-MIT-blue)

## Features

### Core Observability
- **Real-time Metrics Tracking**: Monitor every LLM API call with sub-millisecond precision
- **Cost Analysis**: Track spending across different models with automatic cost calculation
- **Performance Monitoring**: Latency tracking, TTFT (Time To First Token), tokens/second
- **Error Tracking**: Comprehensive error logging with categorization and analysis
- **Cache Analytics**: Monitor cache hit rates and cost savings from semantic caching

### Security Integration
4-layer security system observability:
1. **Llama Guard**: Malicious content detection tracking
2. **RBAC**: Role-based access control monitoring
3. **NeMo Guardrails**: Task validation logging
4. **PII Firewall**: Sensitive data detection and masking events

### Dashboard Features
- **KPI Cards**: Key metrics at a glance (latency, cost, success rate, cache hits)
- **Interactive Charts**: Latency trends, cost breakdowns, request volumes, error rates
- **Live Request Feed**: Real-time table of recent requests with auto-refresh
- **Filters**: Date range, user role, model, and status filters
- **Cost Savings Analysis**: Track savings from intelligent model routing

### Technical Stack

**Backend:**
- FastAPI (async Python web framework)
- PostgreSQL (metrics storage)
- Redis (real-time counters and caching)
- LangFuse (distributed tracing)
- Groq API (LLM provider)

**Frontend:**
- React 18 + TypeScript
- Recharts (data visualization)
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- Vite (build tool)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Groq API key ([get one here](https://console.groq.com))
- LangFuse account ([sign up here](https://langfuse.com))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd LLM_Observibility
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY
# - LANGFUSE_PUBLIC_KEY
# - LANGFUSE_SECRET_KEY
```

3. **Start the services with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize the database**
```bash
# The schema is automatically applied on first start
# Verify it's running:
docker-compose exec postgres psql -U postgres -d llm_observability -c "\dt"
```

5. **Seed test data** (optional)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
python scripts/seed_data.py
```

6. **Access the dashboard**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Python dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Start PostgreSQL and Redis**
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Install Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Ubuntu

# Start services
brew services start postgresql redis  # macOS
sudo systemctl start postgresql redis  # Ubuntu
```

3. **Create database and apply schema**
```bash
createdb llm_observability
psql llm_observability < database/schema.sql
```

4. **Configure environment**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials
```

5. **Start the backend**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Node dependencies**
```bash
cd frontend
npm install
```

2. **Start the development server**
```bash
npm run dev
```

## Usage

### Making Tracked LLM Calls

```python
import httpx

# Example: Make a tracked LLM call
response = httpx.post(
    "http://localhost:8000/api/groq/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "model": "llama-3.1-8b-instant",
        "user_id": "user_123",
        "user_role": "employee",
        "temperature": 0.7,
        "max_tokens": 100
    }
)

print(response.json())
```

### Integrating with Your Existing System

Replace your existing Groq API calls with the instrumented version:

```python
# Before (direct Groq call)
from groq import Groq
client = Groq(api_key="...")
response = client.chat.completions.create(...)

# After (instrumented call)
from app.services.groq_service import groq_service

response = await groq_service.chat_completion(
    messages=[...],
    model="llama-3.1-8b-instant",
    user_id="user_123",
    user_role=UserRole.EMPLOYEE,
)
```

## API Endpoints

### Metrics API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics/dashboard` | GET | Get all dashboard data |
| `/api/metrics/kpis` | GET | Get KPI metrics |
| `/api/metrics/latency-trend` | GET | Get latency trend data |
| `/api/metrics/cost-by-model` | GET | Get cost breakdown |
| `/api/metrics/request-volume` | GET | Get request volume |
| `/api/metrics/recent-requests` | GET | Get recent requests |
| `/api/metrics/models` | GET | Get available models |

### Groq API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/groq/chat/completions` | POST | Basic LLM call with tracking |
| `/api/groq/chat/completions/secured` | POST | LLM call with security layers |

## Database Schema

The system uses a comprehensive schema with the following tables:

- `llm_metrics` - Main metrics table with token counts, latency, costs
- `security_events` - Security layer events and blocks
- `routing_decisions` - AI router model selection logs
- `cache_stats` - Semantic cache hit/miss data
- `pii_events` - PII detection and masking events
- `daily_stats` - Aggregated daily statistics
- `model_stats` - Per-model performance stats
- `rate_limits` - Rate limiting tracking

## Configuration

### Environment Variables

**Backend (`backend/.env`)**
```bash
# Required
GROQ_API_KEY=your_groq_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Optional
API_PORT=8000
DEBUG=True
RATE_LIMIT_PER_MINUTE=60
METRICS_BATCH_SIZE=10
```

**Frontend (`frontend/.env`)**
```bash
VITE_API_URL=http://localhost:8000
```

### Model Pricing

Update pricing in `backend/app/config.py`:

```python
# Groq Pricing (per 1M tokens)
GROQ_LLAMA3_8B_INPUT_COST: float = 0.05
GROQ_LLAMA3_8B_OUTPUT_COST: float = 0.08
# ... add more models
```

## Testing

### Generate Test Traffic

```bash
python scripts/seed_data.py
```

This generates 500 realistic test requests over 7 days with:
- Multiple models and user roles
- Realistic token distributions
- Error scenarios (10% error rate)
- Cache hits (30% hit rate)
- Security events and PII detections

## Performance

- **Async Metrics Logging**: Non-blocking metric writes to database
- **Batch Processing**: Metrics are batched for efficient database writes
- **Redis Caching**: Dashboard data cached for 30 seconds
- **Query Optimization**: Indexed queries and materialized views
- **Connection Pooling**: PostgreSQL connection pool (20-50 connections)

### Capacity

- **Requests/second**: 1000+ (with proper infrastructure)
- **Latency overhead**: <5ms per request
- **Database size**: ~1KB per request (500K requests = ~500MB)

## Monitoring & Maintenance

### Health Check

```bash
curl http://localhost:8000/health
```

### Update Daily Stats

```bash
# Run daily via cron
psql llm_observability -c "SELECT update_daily_stats()"
```

### Backup Database

```bash
pg_dump llm_observability > backup_$(date +%Y%m%d).sql
```

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌───────────┐
│   React     │─────▶│   FastAPI    │─────▶│   Groq    │
│  Dashboard  │      │   Backend    │      │    API    │
└─────────────┘      └──────────────┘      └───────────┘
                            │
                            ├─────▶ PostgreSQL (Metrics)
                            ├─────▶ Redis (Cache)
                            └─────▶ LangFuse (Traces)
```

## Security Considerations

- API keys stored in environment variables
- Rate limiting on all endpoints
- CORS configured for specific origins
- PII detection and masking
- SQL injection prevention via parameterized queries
- Input validation via Pydantic models

## Troubleshooting

### Backend won't start
```bash
# Check if ports are available
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Check database connection
psql -U postgres -d llm_observability
```

### No data showing
```bash
# Seed test data
python scripts/seed_data.py

# Check if backend is running
curl http://localhost:8000/health

# Check database has data
psql llm_observability -c "SELECT COUNT(*) FROM llm_metrics"
```

### Frontend can't connect to backend
```bash
# Verify CORS settings in backend/.env
CORS_ORIGINS=http://localhost:5173

# Check network tab in browser dev tools
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Roadmap

- [ ] PDF export for metrics reports
- [ ] Alerts and notifications
- [ ] Multi-provider support (OpenAI, Anthropic, etc.)
- [ ] Custom metric definitions
- [ ] Team collaboration features
- [ ] Advanced anomaly detection
- [ ] Cost budgets and alerts

## Support

For issues, questions, or contributions, please open a GitHub issue.

---

**Built with ❤️ for the LLM community**
