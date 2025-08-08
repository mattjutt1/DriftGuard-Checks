# DriftGuard Platform

FastAPI service for prompt registry, drift monitoring, and cost/latency budget management.

## Installation

```bash
cd platform/
pip install -e .[dev]
```

## Running

```bash
# Development
make run

# Or directly
uvicorn driftguard.main:app --reload
```

## Testing

```bash
make test
```

## API Endpoints

- `GET /` - Health check
- `POST /api/v1/prompts` - Register a prompt
- `GET /api/v1/prompts` - List prompts
- `GET /api/v1/prompts/{id}` - Get prompt details
- `POST /api/v1/drift/check` - Submit drift check
- `GET /api/v1/drift/history` - Get drift history
- `POST /api/v1/budgets` - Set budget
- `GET /api/v1/budgets/{id}` - Get budget
- `GET /api/v1/metrics` - Platform metrics
