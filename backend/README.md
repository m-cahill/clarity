# CLARITY Backend

FastAPI backend for the CLARITY evaluation instrument.

## Overview

This backend provides:
- `/health` - Service health check endpoint
- `/version` - Version information endpoint

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
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

