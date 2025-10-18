# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Path to your CSV (keep this name or point to your file)
    DATA_PATH: str = "app/data/sample_products.csv"

    # Local FAISS index dir
    VECTOR_INDEX_DIR: str = "app/vector_index"

    # Small, local sentence-transformer (fast + no internet)
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # GenAI model name to use via transformers pipeline (local)
    # Uses gpt2-like small model. If it’s heavy, generator will gracefully fallback.
    GENAI_MODEL: str = "gpt2"

settings = Settings()
