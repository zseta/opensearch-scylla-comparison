import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from dotenv import load_dotenv
load_dotenv()


class ScyllaSearch:
    def __init__(self):
        contact_points = [os.getenv('SCYLLA_URL'), ]
        port = int(os.getenv('SCYLLA_PORT'))
        keyspace = os.getenv('SCYLLA_KEYSPACE')
        username = os.getenv('SCYLLA_USERNAME')
        password = os.getenv('SCYLLA_PASSWORD')

        auth_provider = PlainTextAuthProvider(
            username=username,
            password=password
        )

        self.cluster = Cluster(
            contact_points=contact_points,
            port=port,
            auth_provider=auth_provider
        )

        if keyspace:
            self.session = self.cluster.connect(keyspace)
        else:
            self.session = self.cluster.connect()
        print(self.session)

    def vector_search(self, embedding: list, top_k=5):
        cql = f"""
        SELECT * FROM comments
        ORDER BY text_embedding ANN OF %s 
        LIMIT %s;
        """

        rows = self.session.execute(cql, (embedding, top_k), trace=True)
        results = []
        for row in rows:
            results.append({
                "by": row.by,
                "text": row.text,
                "score": getattr(row, "score", None),
                "time": getattr(row, "time", None),
                "parent": getattr(row, "parent", None),
                "url": getattr(row, "url", None)
            })
        return results


if __name__ == "__main__":
    from embedding_creator import EmbeddingCreator
    scylla = ScyllaSearch()
    
    embedding = EmbeddingCreator().create_embedding("Sample text for embedding")
    results = scylla.vector_search(embedding, top_k=5)
    print(results)
    # Example usage:
    # results = scylla.vector_search([0.1, 0.2, 0.3], top_k=5)
    