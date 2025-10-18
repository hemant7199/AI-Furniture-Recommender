# backend/app/services/analytics.py
import pandas as pd
import re

def compute_analytics(df: pd.DataFrame):
    # prices: prefer numeric column if present
    if "price_num" in df.columns:
        prices = pd.to_numeric(df["price_num"], errors="coerce")
    else:
        prices = pd.to_numeric(df.get("price", pd.Series(dtype="float")), errors="coerce")

    avg_price = float(prices.dropna().mean()) if prices.notna().any() else None
    n_products = int(len(df))

    # top brands
    if "brand" in df.columns:
        top_brands = (
            df["brand"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str[:40]
            .value_counts()
            .head(10)
            .to_dict()
        )
    else:
        top_brands = {}

    # top categories (take first token before | or ,)
    if "categories" in df.columns:
        first_cat = (
            df["categories"]
            .fillna("Unknown")
            .astype(str)
            .apply(lambda s: re.split(r"[|,]", s)[0].strip())
        )
        top_categories = first_cat.value_counts().head(10).to_dict()
    else:
        top_categories = {}

    return {
        "count": n_products,
        "avg_price": avg_price,
        "top_brands": top_brands,
        "top_categories": top_categories,
    }
