# backend/app/services/vector_store.py
from __future__ import annotations
import os
import json
from typing import List, Tuple

import numpy as np
from sklearn.neighbors import NearestNeighbors


class VectorStore:
    """
    Dense vector storage + ANN search using scikit-learn (CPU-only).
    Uses cosine similarity (via 1 - cosine distance) and persists the
    normalized vectors to disk so warm boots are fast.
    """
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)

        # files
        self.vec_path = os.path.join(self.index_dir, "vectors.npy")
        self.meta_path = os.path.join(self.index_dir, "meta.csv")   # keep for compatibility
        self.info_path = os.path.join(self.index_dir, "meta.json")  # small metadata

        # in-memory
        self._vectors: np.ndarray | None = None  # normalized (N, D)
        self._index: NearestNeighbors | None = None
        self._dim: int | None = None
        self._n: int = 0

        self._load_if_exists()

    # -------- persistence helpers --------
    def _save_meta(self):
        info = {"dim": self._dim, "n": self._n}
        with open(self.info_path, "w", encoding="utf-8") as f:
            json.dump(info, f)

    def _load_if_exists(self):
        if not (os.path.isfile(self.vec_path) and os.path.isfile(self.meta_path)):
            return
        try:
            arr = np.load(self.vec_path)
            if arr.ndim == 1:
                # handle empty edge-case robustly
                arr = arr.reshape(0, 0)
            self._vectors = arr
            self._n = int(arr.shape[0])
            self._dim = int(arr.shape[1]) if self._n else 0

            if self._n:
                self._index = NearestNeighbors(
                    n_neighbors=min(10, self._n),
                    algorithm="auto",
                    metric="cosine",
                ).fit(self._vectors)
        except Exception:
            # if anything goes wrong, force rebuild on next request
            self._vectors, self._index, self._dim, self._n = None, None, None, 0

    # -------- public API --------
    def is_built(self) -> bool:
        # keep meta.csv for compatibility with previous FAISS version
        return os.path.isfile(self.vec_path) and os.path.isfile(self.meta_path)

    def build(self, df, embedder, text_cols: List[str]):
        """
        Build index from dataframe `df` using `embedder.encode`.
        - Concats `text_cols` per row
        - Encodes to float32
        - Normalizes rows for cosine
        - Saves vectors to vectors.npy and df to meta.csv (compat)
        """
        texts = df[text_cols].fillna("").astype(str).agg(" ".join, axis=1).tolist()
        embs = embedder.encode(texts)  # shape (N, D)
        embs = np.asarray(embs, dtype="float32")

        # normalize for cosine similarity
        norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-12
        embs = embs / norms

        # persist
        np.save(self.vec_path, embs)
        df.reset_index(drop=True).to_csv(self.meta_path, index=False)

        # fit index
        self._vectors = embs
        self._n, self._dim = int(embs.shape[0]), int(embs.shape[1])
        self._index = NearestNeighbors(
            n_neighbors=min(10, max(1, self._n)),
            algorithm="auto",
            metric="cosine",
        ).fit(self._vectors)

        self._save_meta()

    def search(self, query: str, embedder, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Return list of (row_index, similarity) pairs for the given query.
        Similarity is cosine similarity in [0, 1] (higher is better).
        """
        if self._vectors is None or self._index is None:
            self._load_if_exists()
        if self._vectors is None or self._index is None or self._n == 0:
            raise RuntimeError("VectorStore not built yet.")

        q = embedder.encode([query]).astype("float32")
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)

        k = min(max(1, top_k), self._n)
        dists, idxs = self._index.kneighbors(q, n_neighbors=k, return_distance=True)
        sims = 1.0 - dists[0]  # convert cosine distance -> similarity

        return [(int(i), float(s)) for i, s in zip(idxs[0], sims)]
