import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { login, googleLogin } from "../services/authService";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const googleEnabled = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    }
  }

  async function handleGoogleSuccess(credentialResponse) {
    try {
      await googleLogin(credentialResponse.credential);
      navigate("/dashboard");
    } catch {
      setError("Google sign-in failed.");
    }
  }

  return (
    <div className="grid md:grid-cols-2 min-h-[calc(100vh-73px)]">
      <div className="hidden md:flex flex-col justify-center bg-ink text-white px-14 py-16">
        <p className="font-mono-label text-xs uppercase text-signal mb-4">Welcome Back</p>
        <h2 className="font-display text-3xl font-semibold leading-tight mb-6">
          Real footage moves.<br />Fake footage lies.
        </h2>
        <p className="text-white/60 leading-relaxed mb-8 max-w-sm">
          Log back in to keep checking photos, videos, calls, and voice
          messages before you trust them — whether it's a suspicious
          message from a "relative," a video you're not sure about, or a
          call that just feels off.
        </p>
        <div className="space-y-4 text-sm text-white/60">
          <p>✓ Instant results — no waiting</p>
          <p>✓ Works on photos, video, audio, and live calls</p>
          <p>✓ Your history is saved to your account</p>
        </div>
      </div>

      <div className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <p className="font-mono-label text-xs uppercase text-signal mb-2">Welcome Back</p>
          <h2 className="font-display text-2xl font-semibold mb-6">Login</h2>

          <div className="flex justify-center mb-4">
            {googleEnabled ? <GoogleLogin onSuccess={handleGoogleSuccess} onError={() => setError("Google sign-in failed.")} /> : <p className="text-xs text-ink/40">Google sign-in is not configured.</p>}
          </div>

          <div className="flex items-center gap-3 mb-4 font-mono-label text-[11px] uppercase text-ink/30">
            <div className="flex-1 h-px bg-ink/10" /> Or <div className="flex-1 h-px bg-ink/10" />
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            {error && <p className="text-verdict-fake text-sm">{error}</p>}
            <input
              type="email" placeholder="Email" value={email}
              onChange={(e) => setEmail(e.target.value)} required
              className="border border-ink/20 rounded-sm px-4 py-2.5 text-sm"
            />
            <input
              type="password" placeholder="Password" value={password}
              onChange={(e) => setPassword(e.target.value)} required
              className="border border-ink/20 rounded-sm px-4 py-2.5 text-sm"
            />
            <button
              type="submit"
              className="bg-signal text-white rounded-sm py-2.5 font-medium hover:bg-signal-dark transition-colors"
            >
              Login
            </button>
            <p className="text-center text-sm text-ink/50">
              Don&apos;t have an account? <Link to="/signup" className="text-signal font-medium">Sign up</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;