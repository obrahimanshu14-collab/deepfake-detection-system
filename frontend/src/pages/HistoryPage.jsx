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

  if (loading) return <p style={{ padding: "40px" }}>Loading...</p>;
  if (error) return <p style={{ padding: "40px", color: "red" }}>{error}</p>;

  return (
    <div style={{ padding: "40px", maxWidth: "700px", margin: "0 auto" }}>
      <h1>Prediction History</h1>
      {history.length === 0 ? (
        <p>No predictions yet.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={styles.th}>Filename</th>
              <th style={styles.th}>Label</th>
              <th style={styles.th}>Fake %</th>
              <th style={styles.th}>Date</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td style={styles.td}>{item.filename}</td>
                <td style={styles.td}>{item.label}</td>
                <td style={styles.td}>{(item.fake_probability * 100).toFixed(1)}%</td>
                <td style={styles.td}>{new Date(item.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const styles = {
  th: { textAlign: "left", borderBottom: "2px solid #ddd", padding: "8px" },
  td: { borderBottom: "1px solid #eee", padding: "8px" },
};

export default HistoryPage;