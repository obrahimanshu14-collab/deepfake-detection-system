import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { signup, googleLogin } from "../services/authService";

function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const googleEnabled = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await signup(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed. Please try again.");
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
        <p className="font-mono-label text-xs uppercase text-signal mb-4">Get Started Free</p>
        <h2 className="font-display text-3xl font-semibold leading-tight mb-6">
          See through what's<br />designed to fool you.
        </h2>
        <p className="text-white/60 leading-relaxed mb-8 max-w-sm">
          Deepfake scams, fake videos, and cloned voices are getting harder
          to spot. Create a free account and start checking anything that
          looks — or sounds — a little too convincing.
        </p>
        <div className="space-y-4 text-sm text-white/60">
          <p>✓ 5 free checks, no card required</p>
          <p>✓ Photos, videos, audio, and live calls</p>
          <p>✓ Clear, honest results every time</p>
        </div>
      </div>

      <div className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <p className="font-mono-label text-xs uppercase text-signal mb-2">Create Account</p>
          <h2 className="font-display text-2xl font-semibold mb-6">Sign up</h2>

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
              Sign Up
            </button>
            <p className="text-center text-sm text-ink/50">
              Already have an account? <Link to="/login" className="text-signal font-medium">Login</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;