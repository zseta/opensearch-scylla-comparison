import os
import sys
from opensearchpy import OpenSearch
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def get_client() -> OpenSearch:
    host = os.environ.get("OPENSEARCH_HOST", "localhost")
    port = int(os.environ.get("OPENSEARCH_PORT", 9200))
    return OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=(os.environ.get("OPENSEARCH_USERNAME"), os.environ.get("OPENSEARCH_PASSWORD")),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )
