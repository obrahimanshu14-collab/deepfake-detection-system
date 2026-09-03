import { useEffect, useState } from "react";
import api from "../services/api";

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewing, setViewing] = useState(null);
  const [viewUrl, setViewUrl] = useState(null);
  const [viewLoading, setViewLoading] = useState(false);

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

  async function openItem(item) {
    setViewing(item);
    setViewLoading(true);
    setViewUrl(null);
    try {
      const response = await api.get(`/predict/file/${item.id}`, { responseType: "blob" });
      const url = URL.createObjectURL(response.data);
      setViewUrl(url);
    } catch {
      setViewUrl(null);
    } finally {
      setViewLoading(false);
    }
  }

  function closeModal() {
    if (viewUrl) URL.revokeObjectURL(viewUrl);
    setViewing(null);
    setViewUrl(null);
  }

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
              <th className="border-b border-ink/10 pb-3"></th>
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
                <td className="border-b border-ink/5 py-3">
                  <button onClick={() => openItem(item)} className="text-signal font-medium text-xs">
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {viewing && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6" onClick={closeModal}>
          <div className="bg-white rounded-sm p-5 max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <p className="font-medium text-sm">{viewing.filename}</p>
              <button onClick={closeModal} className="text-ink/40 hover:text-ink text-xl leading-none">×</button>
            </div>

            {viewLoading && <p className="text-ink/50 text-sm">Loading...</p>}
            {!viewLoading && !viewUrl && (
              <p className="text-ink/50 text-sm">This file is no longer available.</p>
            )}
            {!viewLoading && viewUrl && viewing.file_type === "image" && (
              <img src={viewUrl} alt={viewing.filename} className="w-full rounded-sm" />
            )}
            {!viewLoading && viewUrl && (viewing.file_type === "video" || viewing.file_type === "live") && (
              <video src={viewUrl} controls className="w-full rounded-sm" />
            )}
            {!viewLoading && viewUrl && viewing.file_type === "audio" && (
              <audio src={viewUrl} controls className="w-full" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default HistoryPage;