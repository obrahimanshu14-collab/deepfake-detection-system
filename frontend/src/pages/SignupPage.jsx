import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import GoogleAuthButton from "../components/GoogleAuthButton";
import { signup } from "../services/authService";

function SignupPage() {
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
      await signup(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed. Please try again.");
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
          <span className="eyebrow">START WITH TRUST</span>
          <h1>Build confidence in the media you consume.</h1>
          <p>Create your account to analyze images, videos and audio, review previous results, and explore how the detection system reaches its verdict.</p>
          <div className="auth-metrics">
            <div><strong>3</strong><span>Media modes</span></div>
            <div><strong>5</strong><span>Verdict levels</span></div>
            <div><strong>24/7</strong><span>Self-serve access</span></div>
          </div>
        </div>
        <div className="auth-mini-card">
          <span>ANALYSIS PIPELINE</span>
          <strong>Upload → Analyze → Understand</strong>
          <small>Results are presented with transparent confidence bands rather than forcing every input into a binary answer.</small>
        </div>
      </section>

      <section className="auth-panel-wrap">
        <div className="auth-panel">
          <div className="auth-heading">
            <span className="eyebrow">CREATE ACCOUNT</span>
            <h2>Start analyzing in minutes.</h2>
            <p>Use your email or continue securely with Google.</p>
          </div>

          {error && <div className="auth-alert">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-form">
            <label>
              <span>Email address</span>
              <input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
            </label>
            <label>
              <span>Password</span>
              <input type="password" placeholder="At least 8 characters" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} maxLength={128} autoComplete="new-password" />
            </label>
            <button className="auth-submit" type="submit" disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <div className="auth-divider"><span>OR</span></div>
          <GoogleAuthButton mode="signup" onSuccess={() => navigate("/dashboard")} onError={setError} />

          <p className="auth-switch">Already have an account? <Link to="/login">Log in</Link></p>
          <small className="auth-legal">By continuing, you agree to use the service responsibly and only analyze media you are authorized to process.</small>
        </div>
      </section>
    </main>
  );
}

export default SignupPage;
