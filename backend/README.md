# CLARITY Backend

FastAPI backend for the CLARITY evaluation instrument.

## Overview

This backend provides:
- `/health` - Service health check endpoint
- `/version` - Version information endpoint

## Development

The frontend (Vite) proxies `/api` to this backend on **port 8000**. Start the backend before using the counterfactual console or any API from local dev.

```bash
# From repo root: cd backend first
cd backend

# Install dependencies
pip install -e ".[dev]"

# Run the server (default port 8000)
uvicorn app.main:app --reload

# Run tests
pytest --cov=app --cov-report=term-missing
```

## API Endpoints

### GET /health

Returns service health status.

```json
{
  "status": "ok",
  "service": "clarity-backend",
  "version": "0.0.1"
}
```

### GET /version

Returns version information.

```json
{
  "version": "0.0.1",
  "git_sha": null
}
```

## License

Apache-2.0

