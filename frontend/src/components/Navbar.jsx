import { Link, useNavigate } from "react-router-dom";
import { logout, isLoggedIn, isAdmin } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.brand}>Deepfake Detector</Link>
      <div style={styles.links}>
        {isLoggedIn() ? (
          <>
            <Link to="/dashboard" style={styles.link}>Check Image</Link>
            <Link to="/live" style={styles.link}>Live Detection</Link>
            <Link to="/history" style={styles.link}>History</Link>
            {isAdmin() && <Link to="/admin" style={styles.link}>Admin</Link>}
            <button onClick={handleLogout} style={styles.logoutButton}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" style={styles.link}>Login</Link>
            <Link to="/signup" style={styles.link}>Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

const styles = {
  nav: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "14px 30px", borderBottom: "1px solid #eee" },
  brand: { fontWeight: "bold", fontSize: "1.1rem", textDecoration: "none", color: "#111" },
  links: { display: "flex", gap: "18px", alignItems: "center" },
  link: { textDecoration: "none", color: "#2563eb" },
  logoutButton: { padding: "6px 14px", backgroundColor: "#fff", border: "1px solid #ccc", borderRadius: "6px", cursor: "pointer" },
};

export default Navbar;