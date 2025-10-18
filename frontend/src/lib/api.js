// frontend/src/lib/api.js
export const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/**
 * Turn dataset "images" field into a fetchable <img src>.
 * - If full http(s) URL: route via backend /img?url=... proxy
 * - If filename: load from FastAPI static /images/<file>
 */
export function resolveImageUrl(raw) {
  if (!raw) return "";
  const first = String(raw).split("|")[0].split(",")[0].trim();
  if (!first) return "";
  if (/^https?:\/\//i.test(first)) {
    // use image proxy to avoid hotlink blocking
    return `${API_BASE}/img?url=${encodeURIComponent(first)}`;
  }
  const filename = first.replace(/^.*[\\/]/, "");
  return `${API_BASE}/images/${filename}`;
}
