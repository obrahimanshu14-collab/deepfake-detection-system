import { Link, useNavigate } from "react-router-dom";
import { logout, isLoggedIn, isAdmin } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();
  function handleLogout() { logout(); navigate("/login"); }

  const linkStyle = "font-mono-label text-xs uppercase text-ink/60 hover:text-signal transition-colors";

  return (
    <nav className="flex justify-between items-center px-8 py-5 bg-white border-b border-ink/10">
      <Link to="/" className="flex items-center gap-2">
        <span className="w-7 h-7 rounded-sm bg-signal flex items-center justify-center">
          <span className="w-3 h-0.5 bg-white" />
        </span>
        <span className="font-display font-semibold text-lg tracking-tight">Veritas</span>
      </Link>
      <div className="flex gap-7 items-center">
        {isLoggedIn() ? (
          <>
            <Link to="/dashboard" className={linkStyle}>Check</Link>
            <Link to="/live" className={linkStyle}>Live</Link>
            <Link to="/history" className={linkStyle}>History</Link>
            {isAdmin() && <Link to="/admin" className={linkStyle}>Admin</Link>}
            <button onClick={handleLogout} className="font-mono-label text-xs uppercase border border-ink/20 px-4 py-2 rounded-sm hover:border-signal hover:text-signal transition-colors">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className={linkStyle}>Login</Link>
            <Link to="/signup" className="font-mono-label text-xs uppercase bg-signal text-white px-4 py-2 rounded-sm hover:bg-signal-dark transition-colors">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;