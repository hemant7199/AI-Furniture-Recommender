from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from functools import lru_cache
import pandas as pd
import os, urllib.parse, requests, math

from .config import settings
from .services.embeddings import TextEmbedder
from .services.vector_store import VectorStore
from .services.genai import DescriptionGenerator
from .services.analytics import compute_analytics
from .services.nlp import cluster_products

# ----------------- FastAPI App -----------------
app = FastAPI(title="AI-ML Furniture Recommender")

# Allow frontend (Vercel) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check for Render
@app.get("/healthz")
def healthz():
    return {"ok": True}

# Serve local images (if any)
STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), "data", "images")
if os.path.isdir(STATIC_IMG_DIR):
    app.mount("/images", StaticFiles(directory=STATIC_IMG_DIR), name="images")

# ----------------- Helper Functions -----------------
def split_first(raw) -> str:
    if not isinstance(raw, str):
        return ""
    first = raw.split("|")[0].split(",")[0].strip()
    return first.strip().strip("'\"").strip()

def to_price_number(v) -> Optional[float]:
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    for sym in ["₹", "$", "€", "£"]:
        s = s.replace(sym, "")
    try:
        return float(s)
    except:
        return None

def build_click_url(row: pd.Series) -> str:
    for cand in ["product_url", "url", "link", "product_link"]:
        if cand in row and isinstance(row[cand], str) and row[cand].strip():
            return row[cand].strip()
    q = f"{row.get('title','')} {row.get('brand','')}".strip() or str(row.get("uniq_id","furniture"))
    return f"https://www.google.com/search?q={urllib.parse.quote(q)}"

def json_none_if_nan(x):
    try:
        if isinstance(x, float) and math.isnan(x):
            return None
    except:
        pass
    return x if x is not None else None

# ----------------- Data Load -----------------
DATA_PATH = settings.DATA_PATH
required_cols = [
    "uniq_id","title","brand","description","price","categories","images",
    "manufacturer","package dimensions","country_of_origin","material","color"
]

try:
    df = pd.read_csv(DATA_PATH)
    for c in required_cols:
        if c not in df.columns:
            df[c] = ""
    df["price_num"] = df["price"].apply(to_price_number) if "price" in df.columns else None
    df["image_first"] = df["images"].apply(split_first) if "images" in df.columns else ""
except Exception as e:
    raise RuntimeError(f"Failed to load dataset at {DATA_PATH}: {e}")

# ----------------- Lazy Initialization for Render -----------------
@lru_cache
def get_embedder():
    return TextEmbedder(model_name=settings.EMBEDDING_MODEL)

@lru_cache
def get_vs():
    return VectorStore(index_dir=settings.VECTOR_INDEX_DIR)

@lru_cache
def get_genai():
    return DescriptionGenerator()

SKIP_VS_BUILD = os.getenv("SKIP_VS_BUILD", "0") == "1"

def ensure_index_built(df):
    vs = get_vs()
    if vs.is_built() or SKIP_VS_BUILD:
        return
    emb = get_embedder()
    vs.build(
        df,
        emb,
        text_cols=["title","description","categories","brand","material","color"]
    )

# ----------------- Image Resolution -----------------
AMAZON_PREFIX = "https://m.media-amazon.com/images/I/"

def resolve_image_url(val: str, request: Request) -> Optional[str]:
    if not val:
        return None
    v = val.strip().strip("'\"")
    if v.lower().startswith("http://") or v.lower().startswith("https://"):
        return v
    if v.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and "/" not in v:
        return f"{AMAZON_PREFIX}{urllib.parse.quote(v)}"
    local_path = os.path.join(STATIC_IMG_DIR, v)
    if os.path.isfile(local_path):
        base = str(request.base_url).rstrip("/")
        return f"{base}/images/{urllib.parse.quote(v)}"
    return None

# ----------------- Models -----------------
class RecommendRequest(BaseModel):
    query: str
    k: int = 5

class RecommendResponseItem(BaseModel):
    uniq_id: str
    title: str
    image: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    categories: Optional[str] = None
    generated_description: str
    link: Optional[str] = None

class ClusterResponse(BaseModel):
    n_clusters: int
    labels: List[int]

# ----------------- Routes -----------------
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/recommend", response_model=List[RecommendResponseItem])
def recommend(req: RecommendRequest, request: Request):
    ensure_index_built(df)
    vs = get_vs()
    emb = get_embedder()
    genai = get_genai()

    hits = vs.search(req.query, emb, top_k=req.k)
    if not hits:
        raise HTTPException(status_code=404, detail="No products found")

    out = []
    for idx, score in hits:
        row = df.iloc[idx]
        prompt = (
            f"Product: {row.get('title','')}\n"
            f"Brand: {row.get('brand','')}\n"
            f"Category: {row.get('categories','')}\n"
            f"Material: {row.get('material','')}\n"
            f"Color: {row.get('color','')}\n"
            f"Price: {row.get('price','')}\n\n"
            f"User query: {req.query}\n"
            "Write a concise, enticing description (<= 70 words) for why this fits."
        )
        desc = genai.generate(prompt) or ""
        price_val = row.get("price_num", None)
        img_val = row.get("image_first", "")
        img_url = resolve_image_url(img_val, request)

        item = {
            "uniq_id": str(row.get("uniq_id", "")),
            "title": str(row.get("title", "")),
            "image": img_url,
            "price": price_val,
            "brand": json_none_if_nan(row.get("brand", None)),
            "categories": json_none_if_nan(row.get("categories", None)),
            "generated_description": str(desc),
            "link": build_click_url(row),
        }
        out.append(item)

    return out

@app.get("/analytics/summary")
def analytics_summary():
    return compute_analytics(df)

class ClusterRequest(BaseModel):
    n_clusters: int = 8
    text_cols: List[str] = ["title","description","categories"]

@app.post("/nlp/cluster", response_model=ClusterResponse)
def nlp_cluster(req: ClusterRequest):
    labels = cluster_products(df, get_embedder(), req.text_cols, req.n_clusters)
    return {"n_clusters": req.n_clusters, "labels": list(map(int, labels))}

@app.post("/data/upload")
def upload_dataset(file: UploadFile = File(...)):
    global df
    try:
        new_df = pd.read_csv(file.file)
        for c in required_cols:
            if c not in new_df.columns:
                new_df[c] = ""
        new_df["price_num"] = new_df["price"].apply(to_price_number) if "price" in new_df.columns else None
        new_df["image_first"] = new_df["images"].apply(split_first) if "images" in new_df.columns else ""

        df = pd.concat([df, new_df], ignore_index=True)
        ensure_index_built(df)
        return {"rows": int(len(df))}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
