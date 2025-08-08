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

## Environment Configuration

### Required Environment Variables

```bash
# Database configuration
DATABASE_URL=sqlite+aiosqlite:///./driftguard.db

# Offline mode (defaults)
PROMPTOPS_MODE=stub              # Use stub implementations
DISABLE_NETWORK=1                # Block external network access

# Optional: Enable Slack notifications
ALLOW_NETWORK=1                  # Enable network access
SLACK_WEBHOOK_URL=https://...    # Slack webhook URL
```

### Development Setup

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
```

## Database Management

### Initial Setup

```bash
# Run migrations
alembic upgrade head

# Check migration status
alembic heads
```

### Database Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_slack.py -v

# Test with coverage
pytest --cov=driftguard tests/
```

## API Endpoints

### Core Registry

- `GET /` - Health check
- `POST /api/v1/prompts` - Register a prompt version
- `GET /api/v1/prompts` - List registered prompts
- `GET /api/v1/prompts/{id}` - Get specific prompt details

### Monitoring & Alerts

- `POST /api/v1/drift/check` - Submit drift analysis results
- `GET /api/v1/drift/history` - Retrieve drift check history
- `POST /api/v1/budgets` - Set cost/latency budgets
- `GET /api/v1/budgets/{id}` - Get budget configuration
- `POST /api/v1/alerts/test` - Test Slack notification system

### Platform Metrics

- `GET /api/v1/metrics` - Platform usage and health metrics
