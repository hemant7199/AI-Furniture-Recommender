// frontend/src/lib/api.js

// Use Vercel environment variable first, fallback to deployed backend
export const API_BASE =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") || 
  "https://ai-furniture-recommender.onrender.com";

/**
 * Turn dataset "images" field into a fetchable <img src>.
 * - If full http(s) URL: use backend proxy
 * - If filename: load from FastAPI static /images/<file>
 */
export function resolveImageUrl(raw) {
  if (!raw) return "";
  const first = String(raw).split("|")[0].split(",")[0].trim();
  if (!first) return "";

  if (/^https?:\/\//i.test(first)) {
    return first;   // Backend already handles full URLs, no proxy needed
  }

  // Amazon filename only → backend adds base
  return `${API_BASE}/images/${encodeURIComponent(first)}`;
}
