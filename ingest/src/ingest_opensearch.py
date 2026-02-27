import os, sys
from typing import List, Dict
from datetime import datetime
import csv
from opensearchpy import OpenSearch, helpers
from dotenv import load_dotenv
import ast
from opensearch_client import get_client

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ================= CONFIG =================

INDEX_NAME = "hackernews-comments"
BATCH_SIZE = 500  # good default for small datasets

# ========================================


def build_bulk_actions(docs: List[Dict]):
    for doc in docs:
        yield {
            "_index": INDEX_NAME,
            "_id": doc["id"],  # Use the original ID from the document
            "_source": doc,
        }


def ingest_bulk(client: OpenSearch, docs: List[Dict]):
    total = len(docs)
    print(f"Ingesting {total} documents...")

    for i in range(0, total, BATCH_SIZE):
        batch = docs[i:i + BATCH_SIZE]
        success, errors = helpers.bulk(client, build_bulk_actions(batch))

        print(f"Batch {i//BATCH_SIZE + 1}: indexed={success}, errors={len(errors)}")

        if errors:
            print("Sample error:", errors[0])


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default
                
def string_to_float_list(s: str) -> list[float]:
    try:
        return ast.literal_eval(s)
    except (SyntaxError) as e:
        raise SyntaxError(f"Error parsing embedding: {e}")


def str_to_date(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return ts_str

def insert_embeddings(client, csv_path: str):
    docs = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            embedding_string = row.get("text_embedding")
            if embedding_string:
                ts_obj = str_to_date(row.get("timestamp", ""))
                doc = {
                    "id": safe_int(row.get("id", 0)),
                    "title": row.get("title", ""),
                    "url": row.get("url", ""),
                    "text": row.get("text", ""),
                    "text_embedding": string_to_float_list(embedding_string),
                    "dead": row.get("dead", "False").lower() == "true",
                    "by": row.get("by", ""),
                    "score": safe_int(row.get("score", 0)),
                    "time": safe_int(row.get("time", 0)),
                    "timestamp": ts_obj,
                    "type": row.get("type", ""),
                    "parent": safe_int(row.get("parent")) if row.get("parent") else None,
                    "descendants": safe_int(row.get("descendants", 0)),
                    "ranking": safe_int(row.get("ranking", 0)),
                    "deleted": row.get("deleted", "False").lower() == "true",
                }
                docs.append(doc)
    ingest_bulk(client, docs)


LOCAL_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "embeddings", "embeddings_hn_comments_0001.csv")


if __name__ == "__main__":
    client = get_client()
    insert_embeddings(client, LOCAL_CSV_PATH)