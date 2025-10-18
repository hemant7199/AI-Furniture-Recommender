# app/services/vector_store.py
import os
import faiss
import numpy as np
import pandas as pd
from typing import List, Tuple

class VectorStore:
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        self.index_path = os.path.join(index_dir, "faiss.index")
        self.meta_path = os.path.join(index_dir, "meta.csv")
        self.index = None
        self.meta = None

    def is_built(self) -> bool:
        return os.path.exists(self.index_path) and os.path.exists(self.meta_path)

    def build(self, df: pd.DataFrame, embedder, text_cols: List[str]):
        texts = df[text_cols].fillna("").agg(" ".join, axis=1).tolist()
        embs = embedder.encode(texts).astype("float32")

        index = faiss.IndexFlatIP(embs.shape[1])  # cosine because normalized
        index.add(embs)

        faiss.write_index(index, self.index_path)
        df.reset_index(drop=True).to_csv(self.meta_path, index=False)
        self.index = index
        self.meta = df

    def _load(self):
        if self.index is None:
            self.index = faiss.read_index(self.index_path)
        if self.meta is None:
            import pandas as pd
            self.meta = pd.read_csv(self.meta_path)

    def search(self, query: str, embedder, top_k: int = 5) -> List[Tuple[int, float]]:
        self._load()
        q = embedder.encode([query]).astype("float32")
        scores, idxs = self.index.search(q, top_k)
        pairs = []
        for i, s in zip(idxs[0], scores[0]):
            if i == -1:  # faiss padding
                continue
            pairs.append((int(i), float(s)))
        return pairs
