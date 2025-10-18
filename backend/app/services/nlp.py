# app/services/nlp.py
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import List

def cluster_products(df: pd.DataFrame, embedder, text_cols: List[str], n_clusters: int):
    texts = df[text_cols].fillna("").agg(" ".join, axis=1).tolist()
    X = embedder.encode(texts)
    # KMeans on normalized vectors
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = kmeans.fit_predict(X)
    return labels
