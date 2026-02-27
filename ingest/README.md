# opensearch-ingest

Pipeline for downloading raw HackerNews comment data, generating text embeddings, and ingesting into OpenSearch.

## Setup

```bash
uv sync
cp .env.example .env  # then fill in your values
```

## Scripts

### 1. Download raw CSV from S3

Downloads the raw HackerNews comments CSV from a public S3 bucket and saves it to `data/raw/`.

**Required env vars in `.env`:**

```env
S3_BUCKET=your-bucket-name
S3_KEY=path/to/hn_comments_0000.csv
```

**Run:**

```bash
python src/download_raw_csv.py
```

Output: `data/raw/<filename>` (filename is taken from the last segment of `S3_KEY`).

---

### 2. Generate embeddings

Reads the raw CSV from `data/raw/hn_comments_0000.csv`, encodes the `text` column using the `all-MiniLM-L6-v2` sentence-transformer model, and writes the result with an added `text_embedding` column to `data/embeddings/`.

**No env vars required.**

**Run:**

```bash
python src/generate_embeddings.py
```

Output: `data/embeddings/embeddings_hn_comments_0000.csv`

---

### 3. Create the OpenSearch index

Creates the `hackernews-comments` index with the correct field mappings and a `knn_vector` for semantic search.

**Required env vars in `.env`:**

```env
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=your-password
```

**Run:**

```bash
python src/migrate.py
```

Pass `force=True` in code (or re-run after deleting the index manually) to recreate it from scratch.

---

### 4. Ingest embeddings into OpenSearch

Reads the embeddings CSV and bulk-indexes all documents into OpenSearch.

**Required env vars:** same as migrate (see above). Optionally set `EMBEDDINGS_CSV_URL` to a public URL so the CSV is auto-downloaded if not present locally.

**Run:**

```bash
python src/ingest_opensearch.py
```

---

### Typical workflow

```bash
python src/download_raw_csv.py       # 1. fetch raw data
python src/generate_embeddings.py    # 2. compute embeddings
python src/migrate.py                # 3. create OpenSearch index
python src/ingest_opensearch.py      # 4. ingest documents
```

---

## Shared modules

### `src/opensearch_client.py`

Provides a single `get_client()` factory used by all scripts that need an OpenSearch connection. Reads connection details from environment variables (via `.env`).

```python
from opensearch_client import get_client

client = get_client()
```

| Variable | Default | Description |
|---|---|---|
| `OPENSEARCH_HOST` | `localhost` | OpenSearch hostname |
| `OPENSEARCH_PORT` | `9200` | OpenSearch port |
| `OPENSEARCH_USERNAME` | — | Auth username |
| `OPENSEARCH_PASSWORD` | — | Auth password |
