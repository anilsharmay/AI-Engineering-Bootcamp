import numpy as np
from collections import defaultdict
from typing import List, Tuple, Callable, Dict, Any, Optional
from aimakerspace.openai_utils.embedding import EmbeddingModel
import asyncio


def cosine_similarity(vector_a: np.array, vector_b: np.array) -> float:
    """Computes the cosine similarity between two vectors."""
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


class VectorDatabase:
    def __init__(self, embedding_model: EmbeddingModel = None):
        self.vectors = defaultdict(np.array)
        self.metadata = defaultdict(dict)  # Store metadata for each vector
        self.embedding_model = embedding_model or EmbeddingModel()

    def insert(self, key: str, vector: np.array, metadata: Dict[str, Any] = None) -> None:
        self.vectors[key] = vector
        if metadata:
            self.metadata[key] = metadata

    def search(
        self,
        query_vector: np.array,
        k: int,
        distance_measure: Callable = cosine_similarity,
        include_metadata: bool = False,
    ) -> List[Tuple[str, float, Optional[Dict]]]:
        scores = [
            (key, distance_measure(query_vector, vector), self.metadata.get(key, None) if include_metadata else None)
            for key, vector in self.vectors.items()
        ]
        return sorted(scores, key=lambda x: x[1], reverse=True)[:k]

    def search_by_text(
        self,
        query_text: str,
        k: int,
        distance_measure: Callable = cosine_similarity,
        return_as_text: bool = False,
        include_metadata: bool = False,
    ) -> List[Tuple[str, float, Optional[Dict]]]:
        query_vector = self.embedding_model.get_embedding(query_text)
        results = self.search(query_vector, k, distance_measure, include_metadata)
        
        if return_as_text:
            return [result[0] for result in results]
        elif include_metadata:
            return results  # Return (text, score, metadata)
        else:
            # For backward compatibility, return (text, score) when include_metadata=False
            return [(result[0], result[1]) for result in results]

    def retrieve_from_key(self, key: str) -> np.array:
        return self.vectors.get(key, None)

    async def abuild_from_list(self, list_of_text: List[str], metadata_list: List[Dict] = None) -> "VectorDatabase":
        embeddings = await self.embedding_model.async_get_embeddings(list_of_text)
        for i, (text, embedding) in enumerate(zip(list_of_text, embeddings)):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else None
            self.insert(text, np.array(embedding), metadata)
        return self
    
    def build_from_documents_with_metadata(self, documents_with_metadata: List[Dict]) -> "VectorDatabase":
        """
        Build vector database from documents with metadata.
        
        Args:
            documents_with_metadata: List of dicts with 'text' and 'metadata' keys
            
        Returns:
            Self for method chaining
        """
        texts = [doc['text'] for doc in documents_with_metadata]
        metadata_list = [doc.get('metadata', {}) for doc in documents_with_metadata]
        
        # Use async method
        return asyncio.run(self.abuild_from_list(texts, metadata_list))


if __name__ == "__main__":
    list_of_text = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(list_of_text))
    k = 2

    searched_vector = vector_db.search_by_text("I think fruit is awesome!", k=k)
    print(f"Closest {k} vector(s):", searched_vector)

    retrieved_vector = vector_db.retrieve_from_key(
        "I like to eat broccoli and bananas."
    )
    print("Retrieved vector:", retrieved_vector)

    relevant_texts = vector_db.search_by_text(
        "I think fruit is awesome!", k=k, return_as_text=True
    )
    print(f"Closest {k} text(s):", relevant_texts)
