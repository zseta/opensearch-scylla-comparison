import os
import sys
import csv

from sentence_transformers import SentenceTransformer

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ================= CONFIG =================
FILE_NAME = "hn_comments_0001.csv"
INPUT_CSV = os.path.join(PROJECT_ROOT, "data", "raw", FILE_NAME)
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "data", "embeddings", f"embeddings_{FILE_NAME}")

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

OUTPUT_COLUMNS = [
    "id", "title", "url", "text", "text_embedding",
    "dead", "by", "score", "time", "timestamp",
    "type", "parent", "descendants", "ranking", "deleted",
]

# ==========================================


def generate_embeddings(input_path: str, output_path: str) -> None:
    print(f"Loading model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Reading input CSV: {input_path}")
    with open(input_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  Read {len(rows)} rows.")

    texts = [row.get("text", "") for row in rows]

    print(f"Encoding {len(texts)} texts (batch_size={BATCH_SIZE})...")
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)
    print("  Encoding complete.")

    for row, embedding in zip(rows, embeddings):
        row["text_embedding"] = str(embedding.tolist())

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Writing output CSV: {output_path}")
    with open(output_path, newline="", encoding="utf-8", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows)} rows with embeddings.")


if __name__ == "__main__":
    generate_embeddings(INPUT_CSV, OUTPUT_CSV)
