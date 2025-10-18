// frontend/src/pages/Analytics.jsx
import React, { useEffect, useState } from "react";
import { API_BASE } from "../lib/api"; // if your api file is at src/lib/api.js
import MetricCard from "../components/MetricCard";

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [data, setData] = useState({
    count: 0,
    avg_price: null,
    top_brands: {},
    top_categories: {},
  });

  useEffect(() => {
    async function run() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/analytics/summary`);
        if (!res.ok) throw new Error(await res.text());
        const json = await res.json();
        setData(json);
      } catch (e) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    }
    run();
  }, []);

  const topPairs = (obj) =>
    Object.entries(obj || {}).sort((a, b) => b[1] - a[1]);

  const brands = topPairs(data.top_brands).slice(0, 10);
  const cats = topPairs(data.top_categories).slice(0, 10);

  const maxBrand = Math.max(1, ...brands.map(([, v]) => v));
  const maxCat = Math.max(1, ...cats.map(([, v]) => v));

  return (
    <div className="app-shell">
      <div className="header">
        <h1>Analytics</h1>
        <div className="nav">
          <a href="/">Recommend</a>
          <a href="/analytics">Analytics</a>
        </div>
      </div>

      {loading && <div className="assistant-note">Loading analytics…</div>}
      {err && (
        <div className="assistant-note" style={{ color: "#dc2626" }}>
          {err}
        </div>
      )}

      {!loading && !err && (
        <>
          {/* KPI row */}
          <div
            style={{
              display: "grid",
              gap: 12,
              gridTemplateColumns: "repeat( auto-fit, minmax(220px, 1fr) )",
              marginBottom: 16,
            }}
          >
            <MetricCard
              title="Total Products"
              value={data.count?.toLocaleString?.() ?? "—"}
              subtitle="rows in catalog"
            />
            <MetricCard
              title="Average Price"
              value={
                typeof data.avg_price === "number"
                  ? `₹${data.avg_price.toFixed(2)}`
                  : "—"
              }
              subtitle="computed from numeric prices"
            />
          </div>

          {/* Two panels */}
          <div
            style={{
              display: "grid",
              gap: 14,
              gridTemplateColumns: "1fr 1fr",
            }}
          >
            <Panel title="Top Brands (count)">
              <BarList rows={brands} max={maxBrand} />
            </Panel>

            <Panel title="Top Categories (count)">
              <BarList rows={cats} max={maxCat} />
            </Panel>
          </div>
        </>
      )}
    </div>
  );
}

/* ---------- small helpers ---------- */

function Panel({ title, children }) {
  return (
    <div className="card" style={{ gridTemplateColumns: "1fr" }}>
      <div className="content">
        <h3 className="title" style={{ marginBottom: 8 }}>
          {title}
        </h3>
        {children}
      </div>
    </div>
  );
}

function BarList({ rows, max }) {
  if (!rows?.length) return <p className="desc">No data.</p>;
  return (
    <div style={{ display: "grid", gap: 8 }}>
      {rows.map(([label, value]) => {
        const pct = Math.round((value / (max || 1)) * 100);
        return (
          <div key={label}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: 4,
                gap: 8,
              }}
            >
              <span
                style={{
                  fontSize: 13,
                  color: "var(--muted)",
                  inlineSize: "70%",
                  overflowWrap: "anywhere",
                }}
                title={label}
              >
                {label}
              </span>
              <strong style={{ marginLeft: "auto", fontSize: 13 }}>
                {value}
              </strong>
            </div>
            <div
              style={{
                background: "rgba(255,255,255,.08)",
                border: "1px solid #2b364f",
                borderRadius: 9999,
                height: 10,
                overflow: "hidden",
              }}
              aria-hidden
            >
              <div
                style={{
                  width: `${pct}%`,
                  height: "100%",
                  background:
                    "linear-gradient(90deg, var(--accent), #6366f1)",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
