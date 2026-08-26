import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import GoogleAuthButton from "../components/GoogleAuthButton";
import { login } from "../services/authService";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please check your details and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-showcase">
        <Link className="auth-brand" to="/">
          <span className="brand-icon">D</span>
          <span>Deepfake Detector</span>
        </Link>
        <div className="auth-showcase-copy">
          <span className="eyebrow">WELCOME BACK</span>
          <h1>Continue where your last analysis stopped.</h1>
          <p>Access your detection workspace, inspect previous analyses, and use live detection from one secure dashboard.</p>
          <div className="auth-feature-list">
            <div><span>01</span><strong>Image & video analysis</strong><small>Face-aware visual detection with confidence bands.</small></div>
            <div><span>02</span><strong>Audio & signal analysis</strong><small>Additional evidence beyond a single visual frame.</small></div>
            <div><span>03</span><strong>Analysis history</strong><small>Keep your previous results organized in one place.</small></div>
          </div>
        </div>
        <div className="auth-mini-card">
          <span>YOUR WORKSPACE</span>
          <strong>Detect · Review · Verify</strong>
          <small>One account connects your dashboard, history and live analysis experience.</small>
        </div>
      </section>

      <section className="auth-panel-wrap">
        <div className="auth-panel">
          <div className="auth-heading">
            <span className="eyebrow">SECURE LOGIN</span>
            <h2>Welcome back.</h2>
            <p>Sign in with your account or continue with Google.</p>
          </div>

          {error && <div className="auth-alert">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              <span>Email address</span>
              <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
            </label>
            <label>
              <span>Password</span>
              <input type="password" placeholder="Your password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
            </label>
            <button className="auth-submit" type="submit" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="auth-divider"><span>OR</span></div>
          <GoogleAuthButton onSuccess={() => navigate("/dashboard")} onError={setError} />

          <p className="auth-switch">Don't have an account? <Link to="/signup">Create one</Link></p>
          <small className="auth-legal">Google authentication is verified by the backend before a session is created.</small>
        </div>
      </section>
    </main>
  );
}

export default LoginPage;
