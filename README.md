# OpenSearch Demo

Semantic search demo comparing ScyllaDB and OpenSearch for HackerNews comments.

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Copy and fill in environment variables:
   ```bash
   cp ingest/example.env .env
   # edit .env with your ScyllaDB and OpenSearch connection details
   ```

## Start the server

```bash
uv run uvicorn src.main:app --reload
```

The app will be available at http://localhost:8000.

To bind to a specific host or port:
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```
