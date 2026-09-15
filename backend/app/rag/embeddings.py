import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer ({e}). Using mock/deterministic embedder.")
                self._model = False
        return self._model

    def embed_query(self, text: str) -> List[float]:
        if self.model:
            vector = self.model.encode(text, convert_to_numpy=True)
            return vector.tolist()
        return self._pseudo_embed(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            vectors = self.model.encode(texts, convert_to_numpy=True)
            return vectors.tolist()
        return [self._pseudo_embed(t) for t in texts]

    def _pseudo_embed(self, text: str, dim: int = 384) -> List[float]:
        # Fast deterministic hash-based 384-dimensional unit vector
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [(b % 64 - 32) / 32.0 for b in h]
        # Repeat to dim 384
        vec = (vec * ((dim // len(vec)) + 1))[:dim]
        arr = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr.tolist()

embedding_service = EmbeddingService()
