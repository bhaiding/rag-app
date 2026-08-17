from typing import List, Dict

from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import VectorStore


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a user query.

        Args:
            query:
                User's natural-language question.

            k:
                Number of chunks to retrieve.

        Returns:
            List of matching chunks, ordered from most
            similar to least similar.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_embedding = self.embedding_model.embed_query(query)

        results = self.vector_store.search(
            query_embedding,
            k=k,
        )

        return results