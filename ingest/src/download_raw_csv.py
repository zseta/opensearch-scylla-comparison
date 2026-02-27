import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def build_s3_url(bucket: str, key: str) -> str:
    return f"https://{bucket}.s3.amazonaws.com/{key}"


def download_raw_csv() -> Path:
    bucket = os.environ.get("S3_BUCKET")
    key = os.environ.get("S3_KEY")

    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set.")
    if not key:
        raise ValueError("S3_KEY environment variable is not set.")

    url = build_s3_url(bucket, key)
    filename = Path(key).name
    dest = RAW_DIR / filename

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading s3://{bucket}/{key}")
    print(f"  URL  : {url}")
    print(f"  Dest : {dest}")

    def _progress(block_count: int, block_size: int, total_size: int) -> None:
        if total_size > 0:
            downloaded = min(block_count * block_size, total_size)
            pct = downloaded / total_size * 100
            print(f"\r  {downloaded:,} / {total_size:,} bytes ({pct:.1f}%)", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=_progress)
    print()  # newline after progress output
    print(f"Saved to {dest}")
    return dest


if __name__ == "__main__":
    try:
        download_raw_csv()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
