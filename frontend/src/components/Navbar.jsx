import { Link, useLocation, useNavigate } from "react-router-dom";
import { isAdmin, isLoggedIn, logout } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const authenticated = isLoggedIn();
  const admin = isAdmin();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  const linkStyle = "font-mono-label text-xs uppercase text-ink/60 hover:text-signal transition-colors";

  return (
    <nav className="flex justify-between items-center px-5 md:px-8 py-5 bg-white border-b border-ink/10 sticky top-0 z-40">
      <Link to="/" className="flex items-center gap-2" aria-label="Veritas home">
        <span className="w-7 h-7 rounded-sm bg-signal flex items-center justify-center" aria-hidden="true">
          <span className="w-3 h-0.5 bg-white" />
        </span>
        <span className="font-display font-semibold text-lg tracking-tight">Veritas</span>
      </Link>
      <div className="hidden md:flex gap-6 items-center">
        {!authenticated && (
          <>
            <Link to="/privacy" className={linkStyle}>Security</Link>
            <Link to="/login" className={linkStyle}>Login</Link>
            <Link to="/signup" className="font-mono-label text-xs uppercase bg-signal text-white px-4 py-2 rounded-sm hover:bg-signal-dark transition-colors">Sign Up</Link>
          </>
        )}
        {authenticated && (
          <>
            <Link to="/dashboard" className={linkStyle}>Check</Link>
            <Link to="/live" className={linkStyle}>Live</Link>
            <Link to="/history" className={linkStyle}>History</Link>
            <Link to="/developers" className={linkStyle}>API</Link>
            <Link to="/upgrade" className={linkStyle}>Upgrade</Link>
            {admin && <Link to="/admin" className={linkStyle}>Admin</Link>}
            <button onClick={handleLogout} className="font-mono-label text-xs uppercase border border-ink/20 px-4 py-2 rounded-sm hover:border-signal hover:text-signal transition-colors">Logout</button>
          </>
        )}
      </div>
      <div className="md:hidden flex items-center gap-3">
        {authenticated ? (
          <>
            <Link to="/dashboard" className={linkStyle}>Check</Link>
            <Link to="/developers" className={linkStyle}>API</Link>
            <button onClick={handleLogout} className={linkStyle}>Logout</button>
          </>
        ) : (
          <Link to={location.pathname === "/signup" ? "/login" : "/signup"} className={linkStyle}>
            {location.pathname === "/signup" ? "Login" : "Sign Up"}
          </Link>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
