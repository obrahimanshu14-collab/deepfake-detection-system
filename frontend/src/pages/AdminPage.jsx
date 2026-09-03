import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { isAdmin } from "../services/authService";

function AdminPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAdmin()) {
      navigate("/dashboard");
      return;
    }
    async function fetchData() {
      try {
        const [statsRes, usersRes] = await Promise.all([
          api.get("/admin/stats"),
          api.get("/admin/users"),
        ]);
        setStats(statsRes.data);
        setUsers(usersRes.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Could not load admin data.");
      }
    }
    fetchData();
  }, [navigate]);

  if (error) return <p style={{ padding: "40px", color: "red" }}>{error}</p>;
  if (!stats) return <p style={{ padding: "40px" }}>Loading...</p>;

  return (
    <div style={{ padding: "40px", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Admin Console</h1>
      <div style={styles.statsGrid}>
        <div style={styles.statCard}><h3>{stats.total_users}</h3><p>Total Users</p></div>
        <div style={styles.statCard}><h3>{stats.total_predictions}</h3><p>Total Predictions</p></div>
      </div>

      <h2 style={{ marginTop: "30px" }}>Label Breakdown</h2>
      <ul>{Object.entries(stats.label_breakdown).map(([label, count]) => <li key={label}>{label}: {count}</li>)}</ul>

      <h2 style={{ marginTop: "30px" }}>Type Breakdown</h2>
      <ul>{Object.entries(stats.type_breakdown).map(([type, count]) => <li key={type}>{type}: {count}</li>)}</ul>

      <h2 style={{ marginTop: "30px" }}>Users</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr><th style={styles.th}>Email</th><th style={styles.th}>Admin</th><th style={styles.th}>Predictions</th><th style={styles.th}>Joined</th></tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td style={styles.td}>{u.email}</td>
              <td style={styles.td}>{u.is_admin ? "Yes" : "No"}</td>
              <td style={styles.td}>{u.prediction_count}</td>
              <td style={styles.td}>{new Date(u.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  statsGrid: { display: "flex", gap: "20px" },
  statCard: { flex: 1, padding: "20px", border: "1px solid #ddd", borderRadius: "8px", textAlign: "center" },
  th: { textAlign: "left", borderBottom: "2px solid #ddd", padding: "8px" },
  td: { borderBottom: "1px solid #eee", padding: "8px" },
};

export default AdminPage;