// frontend/src/pages/Chat.jsx
import React, { useState } from "react";
import ProductCard from "../components/ProductCard";
import { API_BASE } from "../lib/api";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [k, setK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [messages, setMessages] = useState([]);

  async function send() {
    if (!query.trim()) return;

    setMessages((m) => [...m, { role: "user", text: query }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, k }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResults(data);

      const line = data?.length
        ? `Found ${data.length} products for: "${query}"`
        : "No products found.";
      setMessages((m) => [...m, { role: "assistant", text: line }]);
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Sorry—something went wrong." },
      ]);
    } finally {
      setLoading(false);
      setQuery("");
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    send();
  }

  return (
    <div className="app-shell">
      <div className="header">
        <h1>AI Furniture Recommender</h1>
        <div className="nav">
          <a href="/">Recommend</a>
          <a href="/analytics">Analytics</a>
        </div>
      </div>

      {/* chat bubbles */}
      <div style={{ display: "grid", gap: 10, marginBottom: 10 }}>
        {messages.map((m, idx) =>
          m.role === "user" ? (
            <div key={idx} className="chat-bubble">
              {m.text}
            </div>
          ) : (
            <div key={idx} className="assistant-note">
              {m.text}
            </div>
          )
        )}
      </div>

      {/* input row */}
      <form className="input-row" onSubmit={onSubmit}>
        <input
          type="text"
          placeholder="Ask for a product (e.g., modern wooden chair)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "Searching…" : "Send"}
        </button>
      </form>

      {/* K selector */}
      <div style={{ marginTop: 8, color: "#94a3b8", fontSize: 13 }}>
        Results:{" "}
        <select
          value={k}
          onChange={(e) => setK(parseInt(e.target.value))}
          style={{
            background: "transparent",
            color: "inherit",
            border: "1px solid #334155",
            borderRadius: 6,
            padding: "4px 8px",
          }}
        >
          {[3, 5, 8, 10].map((n) => (
            <option key={n} value={n} style={{ color: "#111827" }}>
              {n}
            </option>
          ))}
        </select>
      </div>

      {/* results */}
      <div className="results-grid">
        {results.map((r) => (
          <ProductCard
            key={r.uniq_id}
            title={r.title}
            brand={r.brand}
            categories={r.categories}
            price={r.price}
            image={r.image}
            description={r.generated_description}
            link={r.link}
          />
        ))}
      </div>
    </div>
  );
}
