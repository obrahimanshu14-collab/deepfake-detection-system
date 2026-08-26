import { useEffect, useMemo, useState } from "react";
import api from "../services/api";
import { isAdmin } from "../services/authService";

function AdminPage() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    if (!isAdmin()) {
      setError("You do not have administrator access.");
      setStats(null);
      return undefined;
    }
    Promise.all([api.get("/admin/stats"), api.get("/admin/users")])
      .then(([statsRes, usersRes]) => {
        if (!active) return;
        setStats(statsRes.data);
        setUsers(usersRes.data);
      })
      .catch((err) => { if (active) setError(err.response?.data?.detail || "Could not load admin data."); });
    return () => { active = false; };
  }, []);

  const totalTypes = Object.values(stats?.type_breakdown || {}).reduce((sum, n) => sum + n, 0) || 1;
  const totalLabels = Object.values(stats?.label_breakdown || {}).reduce((sum, n) => sum + n, 0) || 1;
  const activeUsers = useMemo(() => users.filter((user) => user.prediction_count > 0).length, [users]);

  if (error && !stats) return <main className="app-shell"><div className="inline-error">{error}</div></main>;
  if (!stats) return <main className="app-shell"><div className="empty-panel"><strong>Loading operations console…</strong><p>Fetching system analytics.</p></div></main>;

  return (
    <main className="app-shell">
      <header className="page-app-head">
        <div><span className="eyebrow">OPERATIONS</span><h1>Admin command center.</h1><p>Monitor platform activity, media mix and user adoption from one operational view.</p></div>
        <span className="workspace-badge"><span className="status-dot" /> Admin access</span>
      </header>

      <section className="admin-stats">
        <div className="admin-stat"><span>TOTAL USERS</span><strong>{stats.total_users}</strong></div>
        <div className="admin-stat"><span>TOTAL ANALYSES</span><strong>{stats.total_predictions}</strong></div>
        <div className="admin-stat"><span>ACTIVE USERS</span><strong>{activeUsers}</strong></div>
        <div className="admin-stat"><span>MEDIA EVENTS</span><strong>{totalTypes}</strong></div>
      </section>

      <section className="admin-grid">
        <div className="breakdown"><span className="card-kicker">VERDICTS</span><h2>Outcome distribution</h2>
          {Object.entries(stats.label_breakdown).map(([label, count]) => <div className="breakdown-row" key={label}><span>{label}</span><div className="breakdown-bar"><i style={{ width: `${(count / totalLabels) * 100}%` }} /></div><strong>{count}</strong></div>)}
        </div>
        <div className="breakdown"><span className="card-kicker">MEDIA MIX</span><h2>Analysis volume</h2>
          {Object.entries(stats.type_breakdown).map(([type, count]) => <div className="breakdown-row" key={type}><span>{type}</span><div className="breakdown-bar"><i style={{ width: `${(count / totalTypes) * 100}%` }} /></div><strong>{count}</strong></div>)}
        </div>
      </section>

      <section className="admin-card">
        <div style={{ padding: "22px 24px", borderBottom: "1px solid var(--line)" }}><span className="card-kicker">USER DIRECTORY</span><h2 style={{ margin: "6px 0 0" }}>Accounts and activity</h2></div>
        <div className="table-wrap">
          <table className="product-table"><thead><tr><th>ACCOUNT</th><th>ROLE</th><th>ANALYSES</th><th>JOINED</th></tr></thead><tbody>{users.map((u) => <tr key={u.id}><td><strong>{u.email}</strong></td><td><span className={u.is_admin ? "badge badge-neutral" : "badge badge-success"}>{u.is_admin ? "Admin" : "User"}</span></td><td>{u.prediction_count}</td><td>{new Date(u.created_at).toLocaleDateString()}</td></tr>)}</tbody></table>
        </div>
      </section>
    </main>
  );
}

export default AdminPage;
