import { useEffect, useState } from "react";
import api from "../services/api";

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await api.get("/predict/history");
        setHistory(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Could not load history.");
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  const verdictColor = {
    REAL: "text-verdict-real", "Possibly Real": "text-verdict-real",
    Uncertain: "text-verdict-uncertain",
    "Possibly Fake": "text-verdict-fake", FAKE: "text-verdict-fake",
  };

  if (loading) return <p className="p-10 text-ink/50">Loading...</p>;
  if (error) return <p className="p-10 text-verdict-fake">{error}</p>;

  return (
    <div className="max-w-3xl mx-auto mt-12 px-6">
      <p className="font-mono-label text-xs uppercase text-signal mb-2">Records</p>
      <h1 className="font-display text-2xl font-semibold mb-8">Prediction History</h1>

      {history.length === 0 ? (
        <p className="text-ink/50">No predictions yet.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="font-mono-label text-xs uppercase text-ink/40 text-left">
              <th className="border-b border-ink/10 pb-3">Filename</th>
              <th className="border-b border-ink/10 pb-3">Type</th>
              <th className="border-b border-ink/10 pb-3">Verdict</th>
              <th className="border-b border-ink/10 pb-3">Date</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td className="border-b border-ink/5 py-3">{item.filename}</td>
                <td className="border-b border-ink/5 py-3 uppercase text-ink/50 text-xs">{item.file_type}</td>
                <td className={`border-b border-ink/5 py-3 font-medium ${verdictColor[item.label] || ""}`}>
                  {item.label}
                </td>
                <td className="border-b border-ink/5 py-3 text-ink/50">
                  {new Date(item.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default HistoryPage;