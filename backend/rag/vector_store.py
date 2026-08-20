from typing import List, Dict
from pathlib import Path
import json

import numpy as np
import faiss


class VectorStore:
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim

        self.index = faiss.IndexFlatIP(embedding_dim)

        self.metadata: List[Dict] = []

    def add(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict],
    ) -> None:
        if len(embeddings) != len(metadata):
            raise ValueError(
                "Number of embeddings must match number of metadata items."
            )

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D NumPy array."
            )

        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Expected embedding dimension {self.embedding_dim}, "
                f"got {embeddings.shape[1]}."
            )

        embeddings = embeddings.astype(np.float32)

        self.index.add(embeddings)
        self.metadata.extend(metadata)

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
    ) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Expected query dimension {self.embedding_dim}, "
                f"got {query_embedding.shape[1]}."
            )

        k = min(k, self.index.ntotal)

        scores, indices = self.index.search(
            query_embedding,
            k,
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            results.append(
                {
                    "score": float(score),
                    **self.metadata[index],
                }
            )

        return results

    def save(
        self,
        index_path: str | Path,
        metadata_path: str | Path,
    ) -> None:
        """
        Save FAISS index and metadata to disk.
        """

        index_path = Path(index_path)
        metadata_path = Path(metadata_path)

        index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        metadata_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(index_path),
        )

        with open(
            metadata_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.metadata,
                file,
                indent=2,
            )

    @classmethod
    def load(
        cls,
        index_path: str | Path,
        metadata_path: str | Path,
    ):
        """
        Load a saved FAISS index and metadata from disk.
        """

        index_path = Path(index_path)
        metadata_path = Path(metadata_path)

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {metadata_path}"
            )

        index = faiss.read_index(
            str(index_path)
        )

        with open(
            metadata_path,
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        store = cls(
            embedding_dim=index.d
        )

        store.index = index
        store.metadata = metadata

        return store

    def __len__(self) -> int:
        return self.index.ntotal
    
    def rebuild(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict],
    ) -> None:
        """
        Replace the current FAISS index and metadata
        with a newly rebuilt index.
        """

        if len(embeddings) != len(metadata):
            raise ValueError(
                "Number of embeddings must match number of metadata items."
            )

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D NumPy array."
            )

        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Expected embedding dimension {self.embedding_dim}, "
                f"got {embeddings.shape[1]}."
            )

        embeddings = embeddings.astype(np.float32)

        self.index = faiss.IndexFlatIP(
            self.embedding_dim
        )

        self.index.add(embeddings)

        self.metadata = metadata