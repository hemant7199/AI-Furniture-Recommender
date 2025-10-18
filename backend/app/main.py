# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os, urllib.parse, requests, math

from .config import settings
from .services.embeddings import TextEmbedder
from .services.vector_store import VectorStore
from .services.genai import DescriptionGenerator
from .services.analytics import compute_analytics
from .services.nlp import cluster_products

app = FastAPI(title="AI-ML Furniture Recommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve local images: backend/app/data/images
STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), "data", "images")
if os.path.isdir(STATIC_IMG_DIR):
    app.mount("/images", StaticFiles(directory=STATIC_IMG_DIR), name="images")

# ----------------- helpers -----------------

def split_first(raw) -> str:
    """
    Take first token from 'images' column and sanitize quotes/spaces.
    Handles values like: "url1|url2", "file1.jpg, file2.jpg", "'41abc.jpg '"
    """
    if not isinstance(raw, str):
        return ""
    first = raw.split("|")[0].split(",")[0].strip()
    # strip surrounding quotes and stray characters
    first = first.strip().strip("'\"").strip()
    return first

def to_price_number(v) -> Optional[float]:
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    s = s.replace(",", "")
    for sym in ["₹", "$", "€", "£"]:
        s = s.replace(sym, "")
    try:
        return float(s)
    except:
        return None

def build_click_url(row: pd.Series) -> str:
    # prefer explicit URL columns if present
    for cand in ["product_url", "url", "link", "product_link"]:
        if cand in row and isinstance(row[cand], str) and row[cand].strip():
            return row[cand].strip()
    # fallback: Google search by title + brand
    q = f"{row.get('title','')} {row.get('brand','')}".strip() or str(row.get("uniq_id","furniture"))
    return f"https://www.google.com/search?q={urllib.parse.quote(q)}"

def json_none_if_nan(x):
    """Normalize NaN/NaT to None for JSON safety."""
    try:
        # math.isnan for floats
        if isinstance(x, float) and math.isnan(x):
            return None
    except Exception:
        pass
    if x is None:
        return None
    return x

# ----------------- data load -----------------

DATA_PATH = settings.DATA_PATH
required_cols = [
    "uniq_id","title","brand","description","price","categories","images",
    "manufacturer","package dimensions","country_of_origin","material","color"
]

try:
    df = pd.read_csv(DATA_PATH)

    # Ensure required columns exist
    for c in required_cols:
        if c not in df.columns:
            df[c] = ""

    # price -> numeric
    df["price_num"] = df["price"].apply(to_price_number) if "price" in df.columns else None

    # first/sanitized image token
    df["image_first"] = df["images"].apply(split_first) if "images" in df.columns else ""

except Exception as e:
    raise RuntimeError(f"Failed to load dataset at {DATA_PATH}: {e}")

embedder = TextEmbedder(model_name=settings.EMBEDDING_MODEL)
vs = VectorStore(index_dir=settings.VECTOR_INDEX_DIR)
if not vs.is_built():
    vs.build(df, embedder, text_cols=["title","description","categories","brand","material","color"])
genai = DescriptionGenerator()

# Optional CV import (safe)
try:
    from .models_cv import CVClassifier
    cv = CVClassifier()
except Exception:
    cv = None

# ----------------- models -----------------

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

# ----------------- routes -----------------

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/img")
def proxy_img(url: str = Query(..., description="External image URL to proxy")):
    """Image proxy to bypass hotlink restrictions."""
    if not (url.lower().startswith("http://") or url.lower().startswith("https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")
    try:
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            raise HTTPException(status_code=404, detail="Image not found")
        content_type = r.headers.get("content-type", "image/jpeg")
        return Response(content=r.content, media_type=content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy error: {e}")

@app.post("/recommend", response_model=List[RecommendResponseItem])
def recommend(req: RecommendRequest):
    hits = vs.search(req.query, embedder, top_k=req.k)
    if not hits:
        raise HTTPException(status_code=404, detail="No products found")

    out: List[dict] = []
    for idx, score in hits:
        row = df.iloc[idx]

        # short, helpful blurb
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
        price_val = None if (price_val is None or (isinstance(price_val, float) and math.isnan(price_val))) else float(price_val)

        img_val = row.get("image_first", "")
        img_val = "" if (pd.isna(img_val) if isinstance(img_val, float) else False) else str(img_val).strip().strip("'\"")

        item = {
            "uniq_id": str(row.get("uniq_id", "")),
            "title": str(row.get("title", "")),
            "image": img_val or None,
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
    labels = cluster_products(df, embedder, req.text_cols, req.n_clusters)
    return {"n_clusters": req.n_clusters, "labels": list(map(int, labels))}

@app.post("/data/upload")
def upload_dataset(file: UploadFile = File(...)):
    global df
    try:
        new_df = pd.read_csv(file.file)
        # normalize new chunk too
        for c in required_cols:
            if c not in new_df.columns:
                new_df[c] = ""
        new_df["price_num"] = new_df["price"].apply(to_price_number) if "price" in new_df.columns else None
        new_df["image_first"] = new_df["images"].apply(split_first) if "images" in new_df.columns else ""

        df = pd.concat([df, new_df], ignore_index=True)
        vs.build(df, embedder, text_cols=["title","description","categories","brand","material","color"])
        return {"rows": int(len(df))}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cv/predict")
def cv_predict(image_path: str = "app/data/images/chair1.jpg"):
    if cv is None:
        raise HTTPException(status_code=400, detail="CV model not available")
    label = cv.predict(image_path)
    return {"image_path": image_path, "label": label}
