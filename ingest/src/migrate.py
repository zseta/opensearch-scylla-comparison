"""Create an OpenSearch index equivalent to the provided Cassandra CQL schema.

This module provides a mapping that mirrors the Cassandra table in OpenSearch
and a helper function `create_hackernews_index` which applies the mapping.

Notes:
- Uses the `knn_vector` mapping for `text_embedding` with `inner_product` (dot product).
- Adjust `number_of_shards` / `number_of_replicas` to fit your cluster.
"""
from typing import Any, Dict
import os
import sys
from opensearchpy import OpenSearch
from dotenv import load_dotenv
from opensearch_client import get_client

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def _hackernews_index_body(dimension: int = 384) -> Dict[str, Any]:
    return {
        "settings": {
            "index": {"knn": True},
            "number_of_shards": 1,
            "number_of_replicas": int(os.getenv("OPENSEARCH_REPLICAS", "1")),
        },
        "mappings": {
            "properties": {
                "id": {"type": "long"},
                "title": {"type": "text"},
                "url": {"type": "keyword"},
                "text": {"type": "text"},
                "text_embedding": {
                    "type": "knn_vector",
                    "dimension": dimension,
                    "method": {
                        "name": "hnsw",
                        "space_type": "innerproduct",
                        "engine": "lucene",
                        "parameters": {"ef_construction": 512, "m": 16},
                    },
                },
                "dead": {"type": "boolean"},
                "by": {"type": "keyword"},
                "score": {"type": "integer"},
                "time": {"type": "long"},
                "timestamp": {"type": "date"},
                "type": {"type": "keyword"},
                "parent": {"type": "long"},
                "descendants": {"type": "integer"},
                "ranking": {"type": "integer"},
                "deleted": {"type": "boolean"},
            }
        },
    }


def create_hackernews_index(
    client: OpenSearch,
    index_name: str = "hackernews-comments",
    dimension: int = 384,
    force: bool = False,
) -> Dict[str, Any]:
    """Create the OpenSearch index for hackernews comments.

    Args:
        client: an initialized `opensearchpy.OpenSearch` client.
        index_name: name of the index to create.
        dimension: vector dimension for `text_embedding`.
        force: if True and the index exists, delete and recreate it.

    Returns the response from OpenSearch's `indices.create` or a dict
    indicating the index already exists when `force` is False.
    """
    if client.indices.exists(index=index_name):
        if not force:
            return {"acknowledged": True, "result": "exists"}
        client.indices.delete(index=index_name)

    body = _hackernews_index_body(dimension=dimension)
    return client.indices.create(index=index_name, body=body)


if __name__ == "__main__":

    client = get_client()

    resp = create_hackernews_index(client, index_name="hackernews-comments", force=False)
    print(resp)
