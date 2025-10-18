// frontend/src/components/ProductCard.jsx
import React from "react";
import { resolveImageUrl } from "../lib/api";

export default function ProductCard({
  title,
  brand,
  categories,
  price,
  image,
  description,
  link,
}) {
  const img = resolveImageUrl(image);

  // fallback link if backend didn't supply one
  const clickUrl =
    link ||
    `https://www.google.com/search?q=${encodeURIComponent(
      `${title || ""} ${brand || ""}`.trim()
    )}`;

  return (
    <a className="card" href={clickUrl} target="_blank" rel="noreferrer">
      <div className="media">
        {img ? (
          <img
            src={img}
            alt={title}
            loading="lazy"
            onError={(e) => {
              e.currentTarget.src = "https://placehold.co/300x220?text=No+Image";
            }}
          />
        ) : (
          <img
            src="https://placehold.co/300x220?text=No+Image"
            alt="placeholder"
          />
        )}
      </div>

      <div className="content">
        <h3 className="title">{title}</h3>

        <div className="meta">
          {brand ? <span className="badge">{brand}</span> : null}
          {categories ? (
            <span className="badge badge-soft">
              {String(categories).split(/[|,/]/)[0].trim()}
            </span>
          ) : null}
          {typeof price === "number" ? (
            <span className="price">₹{price.toLocaleString()}</span>
          ) : null}
        </div>

        <p className="desc">{description}</p>
      </div>
    </a>
  );
}
