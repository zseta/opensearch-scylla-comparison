import os
import sys
import time

# Ensure the src/ directory is on the path when running as `uvicorn src.main:app`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from scylla_search import ScyllaSearch
from embedding_creator import EmbeddingCreator
from opensearch_search import OpenSearchSearch

app = FastAPI()

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# add templates
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

embedding_creator = EmbeddingCreator()
scylla = ScyllaSearch()
open_search = OpenSearchSearch()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

    
@app.get("/search/{database}", response_class=HTMLResponse)
async def search_database(request: Request, database: str, q: str = ""):
    if database not in ["scylladb", "opensearch"]:
        return HTMLResponse(status_code=404, content=f"`{database}` not supported")
    embedding = embedding_creator.create_embedding(q)

    latency = None
    results = None
    if database == "scylladb":
        start = time.time()
        results = scylla.vector_search(embedding, top_k=3)
        latency = int((time.time() - start) * 1000)  # ms

    elif database == "opensearch":
        start = time.time()
        results = open_search.vector_search(embedding, top_k=3)
        latency = int((time.time() - start) * 1000)  # ms

    context = {"request": request, "results": results, "latency": latency}
    return templates.TemplateResponse(
        f"partials/results_container_{'A' if database == 'scylladb' else 'B'}.html",
        context)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
