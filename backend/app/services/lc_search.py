# backend/app/services/lc_search.py

from __future__ import annotations

from typing import List, Tuple
import os
import pandas as pd

# Use community package (works with langchain 0.2.x)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS as LCFAISS
from langchain_community.vectorstores import Pinecone as LCPinecone
from langchain.docstore.document import Document

# Pinecone client is optional (only used if USE_PINECONE=True)
from pinecone import Pinecone, ServerlessSpec


class LCRetriever:
    """
    LangChain-based retriever that can back onto FAISS (local) or Pinecone (cloud),
    depending on flags passed from settings.

    - build(df, text_cols): builds/refreshes the index from a DataFrame
    - search(query, top_k): returns list of (row_index, score) pairs
    """

    def __init__(
        self,
        index_dir: str,
        use_pinecone: bool,
        pinecone_api_key: str | None,
        pinecone_index: str | None,
        pinecone_cloud: str | None,
        pinecone_region: str | None,
        emb_model: str,
    ) -> None:
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)

        self.use_pinecone = use_pinecone
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index = pinecone_index
        self.pinecone_cloud = pinecone_cloud
        self.pinecone_region = pinecone_region

        # HF sentence encoder used by both FAISS and Pinecone paths
        self.embeddings = HuggingFaceEmbeddings(model_name=emb_model)

        self.db = None  # LangChain VectorStore instance

    # -----------------------------
    # Build / Load
    # -----------------------------
    def build(self, df: pd.DataFrame, text_cols: List[str]) -> None:
        """
        Build (or rebuild) the vector store from a dataframe.
        text_cols are concatenated into one text string per row.
        """
        texts = (df[text_cols].fillna("").agg(". ".join, axis=1)).tolist()
        docs = [Document(page_content=t, metadata={"row_id": i}) for i, t in enumerate(texts)]

        if self.use_pinecone:
            if not self.pinecone_api_key or not self.pinecone_index:
                raise RuntimeError("Pinecone selected but API key or index name not provided.")

            pc = Pinecone(api_key=self.pinecone_api_key)

            # Create index if it doesn't exist
            existing = [i.name for i in pc.list_indexes()]
            if self.pinecone_index not in existing:
                dim = len(self.embeddings.embed_query("dimension probe"))
                pc.create_index(
                    name=self.pinecone_index,
                    dimension=dim,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=self.pinecone_cloud or "aws",
                                        region=self.pinecone_region or "us-east-1"),
                )

            # Build LC vectorstore over Pinecone
            self.db = LCPinecone.from_documents(
                docs, self.embeddings, index_name=self.pinecone_index
            )
        else:
            # Local FAISS vectorstore
            self.db = LCFAISS.from_documents(docs, self.embeddings)
            # Persist for later loads
            self.db.save_local(self.index_dir)

    def load(self) -> None:
        """
        Load the vector store into memory if not already loaded.
        """
        if self.db is not None:
            return

        if self.use_pinecone:
            if not self.pinecone_api_key or not self.pinecone_index:
                raise RuntimeError("Pinecone selected but API key or index name not provided.")

            pc = Pinecone(api_key=self.pinecone_api_key)
            index = pc.Index(self.pinecone_index)
            # For Pinecone, LangChain wraps an existing index
            self.db = LCPinecone(index, self.embeddings, text_key="text")
        else:
            # allow_dangerous_deserialization is required for FAISS load in LC 0.2.x
            self.db = LCFAISS.load_local(
                self.index_dir, self.embeddings, allow_dangerous_deserialization=True
            )

    # -----------------------------
    # Search
    # -----------------------------
    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Perform similarity search and return a list of (row_id, score) tuples.
        Lower score is better (cosine distance).
        """
        self.load()
        results = self.db.similarity_search_with_score(query, k=top_k)
        # Extract dataframe row indices stored in metadata
        return [(int(doc.metadata["row_id"]), float(score)) for doc, score in results]
