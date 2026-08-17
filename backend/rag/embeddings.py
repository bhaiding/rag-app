from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        Load a sentence-transformers embedding model.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of strings into embedding vectors.

        Args:
            texts:
                List of text strings to embed.

        Returns:
            NumPy array of shape:
            (number_of_texts, embedding_dimension)
        """

        if not texts:
            return np.empty((0, 0))

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query.

        Args:
            query:
                User question or search query.

        Returns:
            One embedding vector.
        """

        embedding = self.embed_texts([query])

        return embedding[0]


if __name__ == "__main__":
    model = EmbeddingModel()

    test_texts = [
        "Linear probes can detect deception in language models.",
        "The weather is sunny today.",
        "Internal activations may contain information about deceptive behavior.",
    ]

    embeddings = model.embed_texts(test_texts)

    print(f"Number of texts: {len(test_texts)}")
    print(f"Embedding shape: {embeddings.shape}")
    print()

    for i, vector in enumerate(embeddings):
        print(f"Text {i}:")
        print(test_texts[i])
        print(f"First 10 values: {vector[:10]}")
        print()