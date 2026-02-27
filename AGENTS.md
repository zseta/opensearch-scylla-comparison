## OpenSearch commands

### Cloud auth/runtime notes (AWS VPC)
- Prefer IAM role credentials on EC2/ECS/Lambda (no static key env vars).
- Required env vars for scripts/app:
  - `OPENSEARCH_HOST` (domain endpoint host, with or without `https://`)
  - `OPENSEARCH_REGION` (for SigV4)
  - Optional: `OPENSEARCH_PORT` (defaults to `443`)
  - Optional: `OPENSEARCH_SERVICE` (defaults to `es`)
  - Optional: `OPENSEARCH_IAM_ROLE_ONLY` (defaults to `true`)
- Ensure SG rules allow runtime -> OpenSearch on `443` and IAM policies allow `es:ESHttp*`.

### Get a list of indices
uv run awscurl --service es --region us-east-1 https://search-test-opensearch-hisocsvm67fv6dyw2so6aavf6u.us-east-1.es.amazonaws.com/_cat/indices?v

### Get schema(mapping) of index
uv run awscurl --service es --region us-east-1 \
https://search-test-opensearch-hisocsvm67fv6dyw2so6aavf6u.us-east-1.es.amazonaws.com/hackernews-comments/_mapping?pretty

### Query - vector search
uv run awscurl --service es --region us-east-1 \
  -XPOST "https://search-test-opensearch-hisocsvm67fv6dyw2so6aavf6u.us-east-1.es.amazonaws.com/hackernews-comments/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 5,
    "query": {
      "knn": {
        "text_embedding": {
          "vector": [0.1, 0.2, 0.3],
          "k": 5
        }
      }
    }
  }'

### Query - limit 1

uv run awscurl --service es --region us-east-1 \
  -XPOST "https://search-test-opensearch-hisocsvm67fv6dyw2so6aavf6u.us-east-1.es.amazonaws.com/hackernews-comments/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 2,
    "query": { "match_all": {} }
  }'



### Query - count of all rows in index
uv run awscurl --service es --region us-east-1 \
  -XPOST "https://search-test-opensearch-hisocsvm67fv6dyw2so6aavf6u.us-east-1.es.amazonaws.com/hackernews-comments/_count?pretty" \
  -H 'Content-Type: application/json' \
  -d '{ "query": { "match_all": {} } }'

## Docker ingestion container

### Build image
docker build -f ingest/Dockerfile -t opensearch-ingest .

### Start container (runs migration automatically on startup)
docker run -d --name opensearch-ingest --env-file .env opensearch-ingest

### Run ingestion manually from outside the container
docker exec -it opensearch-ingest python ingest/ingest_opensearch.py

### Inspect startup/migration logs
docker logs opensearch-ingest

### Stop and remove container
docker rm -f opensearch-ingest