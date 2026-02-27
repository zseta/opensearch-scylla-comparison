# OpenSearch Demo

Semantic search demo comparing ScyllaDB and OpenSearch for HackerNews comments.

## Screenshot

![Demo](/docs/images/demo.png)

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

## Run OpenSearch locally

```bash
docker run -d \
  --name opensearch \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=Pa\$\$word1" \
  opensearchproject/opensearch:3
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
