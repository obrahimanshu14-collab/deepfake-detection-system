import { Link, useNavigate } from "react-router-dom";
import { logout, isLoggedIn, isAdmin } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="site-nav">
      <Link to="/" className="brand-mark">
        <span className="brand-icon">D</span>
        <span>Deepfake Detector</span>
      </Link>

      <div className="nav-links public-links">
        <Link to="/technology">Technology</Link>
        <Link to="/how-it-works">How it works</Link>
        <Link to="/research">Research</Link>
        <Link to="/security">Security</Link>
      </div>

      <div className="nav-links account-links">
        {isLoggedIn() ? (
          <>
            <Link to="/dashboard">Analyze</Link>
            <Link to="/live">Live</Link>
            <Link to="/history">History</Link>
            {isAdmin() && <Link to="/admin">Admin</Link>}
            <button onClick={handleLogout} className="nav-button">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup" className="nav-cta">Get started</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
