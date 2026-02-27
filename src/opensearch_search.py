from dotenv import load_dotenv
from opensearch_client import get_client
load_dotenv()

class OpenSearchSearch:
    def __init__(self):
        self.index = "hackernews-comments"
        self.client = get_client()
        
    def count_items(self):
        query = { "query": { "match_all": {} } }
        response = self.client.count(index=self.index, body=query)
        #print(response)
        return response.get('count', 0)

    def vector_search(self, embedding: list[float], top_k=5):
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    "text_embedding": {
                        "vector": embedding,
                        "k": top_k
                    }
                }
            },
            "_source": ["by", "text", "score", "time", "parent", "url"]
        }
        response = self.client.search(index=self.index, body=query)
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            source = hit.get('_source', {})
            results.append({
                "by": source.get("by"),
                "text": source.get("text"),
                "score": source.get("score"),
                "time": source.get("time"),
                "parent": source.get("parent"),
                "url": source.get("url")
            })
        return results

if __name__ == "__main__":
    from embedding_creator import EmbeddingCreator
    opensearch = OpenSearchSearch()
    embedding = EmbeddingCreator().create_embedding("I like the idea")
    results = opensearch.vector_search(embedding, top_k=5)
    print(results)
