# app/services/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import os

# Avoid non-deterministic parallel tokenization behavior
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

def _l2_normalize(x: np.ndarray) -> np.ndarray:
    """
    Safe L2 normalization for either (d,) or (n, d) arrays.
    Returns float32 for compatibility with most vector indexes.
    """
    x = x.astype("float32", copy=False)
    if x.ndim == 1:
        denom = float(np.linalg.norm(x)) or 1e-12
        return x / denom
    denom = np.linalg.norm(x, axis=1, keepdims=True)
    denom = np.where(denom == 0, 1e-12, denom)
    return x / denom

class TextEmbedder:
    def __init__(self, model_name: str):
        # Load once; caller already caches the instance via @lru_cache
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Returns L2-normalized embeddings (float32).
        We disable internal normalization and do it ourselves to ensure
        consistent behavior across library/model versions.
        """
        if isinstance(texts, str):
            texts = [texts]

        embs = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,  # we normalize explicitly below
        )
        return _l2_normalize(embs)
