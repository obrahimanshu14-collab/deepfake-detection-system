import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { login, googleLogin } from "../services/authService";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

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
    <div className="max-w-sm mx-auto mt-16 px-6">
      <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">Welcome Back</p>
      <h2 className="font-display text-2xl font-semibold text-center mb-6">Login</h2>

      <div className="flex justify-center mb-4">
        <GoogleLogin onSuccess={handleGoogleSuccess} onError={() => setError("Google sign-in failed.")} />
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
          Don&apos;t have an account? <a href="/signup" className="text-signal font-medium">Sign up</a>
        </p>
      </form>
    </div>
  );
}

export default LoginPage;