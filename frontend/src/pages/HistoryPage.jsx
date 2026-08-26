import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

function verdictClass(label) {
  if (label === "REAL" || label === "Possibly Real") return "badge badge-success";
  if (label === "FAKE" || label === "Possibly Fake") return "badge badge-danger";
  return "badge badge-neutral";
}

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api.get("/predict/history")
      .then((response) => { if (active) setHistory(response.data); })
      .catch((err) => { if (active) setError(err.response?.data?.detail || "Could not load history."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const filtered = useMemo(() => history.filter((item) => {
    const matchesType = filter === "all" || item.file_type === filter;
    const matchesQuery = !query.trim() || item.filename.toLowerCase().includes(query.trim().toLowerCase());
    return matchesType && matchesQuery;
  }), [history, filter, query]);

  if (loading) return <main className="app-shell"><div className="empty-panel"><strong>Loading your analyses…</strong><p>Fetching your private history.</p></div></main>;

  return (
    <main className="app-shell">
      <header className="page-app-head">
        <div>
          <span className="eyebrow">YOUR ANALYSIS HISTORY</span>
          <h1>Every check, organized.</h1>
          <p>Review previous media checks, confidence scores and timestamps from your workspace.</p>
        </div>
        <Link className="hero-primary" to="/dashboard">New analysis →</Link>
      </header>

      {error && <div className="inline-error">{error}</div>}

      <div className="data-toolbar">
        {["all", "image", "video", "audio"].map((type) => (
          <button key={type} className={`filter-button ${filter === type ? "active" : ""}`} onClick={() => setFilter(type)}>{type === "all" ? "All" : `${type[0].toUpperCase()}${type.slice(1)}`}</button>
        ))}
        <input className="history-search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search filename…" aria-label="Search history" />
      </div>

      <section className="history-card">
        {filtered.length === 0 ? (
          <div className="empty-panel"><strong>{history.length ? "No matching analyses" : "No analyses yet"}</strong><p>{history.length ? "Try another filter or search term." : "Start with an image, video or audio analysis."}</p></div>
        ) : (
          <div className="table-wrap">
            <table className="product-table">
              <thead><tr><th>MEDIA</th><th>VERDICT</th><th>FAKE PROBABILITY</th><th>DATE</th></tr></thead>
              <tbody>
                {filtered.map((item) => (
                  <tr key={item.id}>
                    <td><strong>{item.filename}</strong><div className="table-sub">{item.file_type}</div></td>
                    <td><span className={verdictClass(item.label)}>{item.label}</span></td>
                    <td>{(Number(item.fake_probability || 0) * 100).toFixed(1)}%</td>
                    <td>{new Date(item.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default HistoryPage;
