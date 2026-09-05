import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

function DeveloperPage() {
  const [organizationName, setOrganizationName] = useState("");
  const [keyName, setKeyName] = useState("Production");
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  const apiBase = api.defaults.baseURL || "http://127.0.0.1:8000";
  const curl = useMemo(
    () =>
      `curl -X POST "${apiBase}/v1/predict/image" -H "X-API-Key: ${
        apiKey || "vrs_live_your_key"
      }" -F "file=@sample.jpg"`,
    [apiBase, apiKey]
  );

  async function createKey(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setApiKey("");
    setCopied(false);
    try {
      const { data } = await api.post("/v1/api-keys", {
        organization_name: organizationName,
        name: keyName,
      });
      setApiKey(data.api_key);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create API key.");
    } finally {
      setLoading(false);
    }
  }

  async function copyKey() {
    if (!apiKey) return;
    await navigator.clipboard.writeText(apiKey);
    setCopied(true);
  }

  return (
    <main className="min-h-screen bg-mist px-5 md:px-10 py-12">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-12">
          <div>
            <p className="font-mono-label text-xs uppercase text-signal mb-3">Developer Platform</p>
            <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight">
              Integrate Veritas into your product.
            </h1>
            <p className="mt-4 max-w-2xl text-ink/60 leading-relaxed">
              Provision a server-side API key and call the same detection engines from another product, workflow, or organization.
            </p>
          </div>
          <Link to="/dashboard" className="font-mono-label text-xs uppercase text-signal">
            ← Back to detection
          </Link>
        </div>

        <section className="grid lg:grid-cols-[0.85fr_1.15fr] gap-8">
          <div className="bg-white border border-ink/10 rounded-sm p-7">
            <p className="font-mono-label text-[11px] uppercase text-ink/40 mb-2">01 / Provision</p>
            <h2 className="font-display text-2xl font-semibold mb-6">Create an integration key</h2>
            <form onSubmit={createKey} className="space-y-4">
              <label className="block text-sm">
                <span className="block mb-2 text-ink/60">Organization</span>
                <input
                  value={organizationName}
                  onChange={(event) => setOrganizationName(event.target.value)}
                  required
                  minLength={2}
                  className="w-full border border-ink/15 rounded-sm px-4 py-3 outline-none focus:border-signal"
                  placeholder="Acme Verification"
                />
              </label>
              <label className="block text-sm">
                <span className="block mb-2 text-ink/60">Key name</span>
                <input
                  value={keyName}
                  onChange={(event) => setKeyName(event.target.value)}
                  required
                  minLength={2}
                  className="w-full border border-ink/15 rounded-sm px-4 py-3 outline-none focus:border-signal"
                  placeholder="Production"
                />
              </label>
              {error && <p className="text-sm text-verdict-fake">{error}</p>}
              <button
                disabled={loading}
                className="w-full bg-signal text-white py-3 rounded-sm font-medium disabled:opacity-50"
              >
                {loading ? "Provisioning…" : "Generate API Key"}
              </button>
            </form>

            {apiKey && (
              <div className="mt-6 border border-signal/30 bg-signal/5 rounded-sm p-4">
                <p className="font-mono-label text-[10px] uppercase text-signal mb-2">Shown once</p>
                <code className="text-xs break-all text-ink">{apiKey}</code>
                <button onClick={copyKey} className="mt-3 text-xs font-medium text-signal">
                  {copied ? "Copied" : "Copy key"}
                </button>
              </div>
            )}
          </div>

          <div className="bg-ink text-white rounded-sm p-7 overflow-hidden">
            <p className="font-mono-label text-[11px] uppercase text-signal mb-2">02 / Call</p>
            <h2 className="font-display text-2xl font-semibold mb-6">One API contract</h2>
            <div className="space-y-5 text-sm text-white/65 leading-relaxed">
              <p><span className="text-white">Image:</span> <code>POST /v1/predict/image</code></p>
              <p><span className="text-white">Video:</span> <code>POST /v1/predict/video</code></p>
              <p><span className="text-white">Audio:</span> <code>POST /v1/predict/audio</code></p>
              <p><span className="text-white">Auth:</span> <code>X-API-Key</code></p>
            </div>
            <pre className="mt-6 bg-black/30 border border-white/10 rounded-sm p-4 text-[11px] leading-relaxed overflow-x-auto whitespace-pre-wrap">
              {curl}
            </pre>
          </div>
        </section>

        <section className="grid md:grid-cols-3 gap-5 mt-8">
          {[
            ["Predict", "Normalized verdict, fake probability, and model metadata."],
            ["Privacy", "Developer API calls do not retain raw uploaded media after inference."],
            ["Control", "API keys use hashed storage and a configurable rolling 24-hour limit."],
          ].map(([title, body]) => (
            <div key={title} className="border border-ink/10 bg-white p-6">
              <h3 className="font-display text-lg font-semibold mb-2">{title}</h3>
              <p className="text-sm text-ink/55 leading-relaxed">{body}</p>
            </div>
          ))}
        </section>

        <section className="mt-10 border-t border-ink/10 pt-8 text-sm text-ink/55">
          Full OpenAPI documentation is available at <code>/docs</code>. API keys must stay on an organization's server; never ship them in browser JavaScript.
        </section>
      </div>
    </main>
  );
}

export default DeveloperPage;
