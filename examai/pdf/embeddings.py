import numpy as np
from typing import List
from examai.utils.logger import logger

class EmbeddingsGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy loads the model so that basic CLI commands launch instantly."""
        if self._model is None:
            logger.info(f"Loading SentenceTransformers model: {self.model_name}")
            from sentence_transformers import SentenceTransformer
            # Disable torch warnings
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generates a numpy matrix of embeddings for a list of texts."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.astype(np.float32)

# Singleton embeddings helper
embeddings_generator = EmbeddingsGenerator()
