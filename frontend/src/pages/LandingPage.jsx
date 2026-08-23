import { useNavigate } from "react-router-dom";

function LandingPage() {
  const navigate = useNavigate();

  const inputs = [
    { label: "INPUT — IMAGE", desc: "Single-frame texture and frequency analysis via a transfer-learned CNN." },
    { label: "INPUT — VIDEO", desc: "Frame sampling combined with physiological signal analysis (rPPG)." },
    { label: "INPUT — AUDIO", desc: "Spectrogram-based detection of synthetic and cloned speech." },
    { label: "INPUT — LIVE", desc: "Continuous webcam scanning with a real-time running verdict." },
  ];

  return (
    <div>
      <section className="max-w-6xl mx-auto px-8 pt-20 pb-24 grid md:grid-cols-2 gap-16 items-center">
        <div>
          <p className="font-mono-label text-xs uppercase text-signal mb-4">Verification Engine</p>
          <h1 className="font-display text-5xl font-semibold leading-tight mb-6">
            Scan for what's<br />engineered to deceive.
          </h1>
          <p className="text-lg text-ink/70 leading-relaxed mb-8 max-w-md">
            Veritas analyzes images, video, audio, and live streams for the
            statistical fingerprints synthetic media leaves behind — and
            tells you exactly how confident it is.
          </p>
          <div className="flex gap-4">
            <button onClick={() => navigate("/signup")}
              className="bg-signal text-white px-7 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors">
              Start Free Scan
            </button>
            <button onClick={() => navigate("/login")}
              className="border border-ink/20 px-7 py-3 rounded-sm font-medium hover:border-signal transition-colors">
              Login
            </button>
          </div>
        </div>

        <div className="relative rounded-sm border border-ink/10 bg-white p-3 shadow-sm">
          <div className="relative overflow-hidden rounded-sm">
            <img
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&h=600&fit=crop"
              alt="Sample scan subject"
              className="w-full h-96 object-cover"
            />
            <div className="absolute left-0 right-0 h-px bg-signal shadow-[0_0_12px_2px_rgba(11,114,133,0.8)] scan-line" />
          </div>
          <div className="flex justify-between items-center pt-3 px-1">
            <span className="font-mono-label text-[11px] uppercase text-ink/40">Example analysis</span>
            <span className="font-mono-label text-[11px] uppercase text-verdict-real">Real — 96.2%</span>
          </div>
        </div>
      </section>

      <section className="border-t border-ink/10 bg-white">
        <div className="max-w-6xl mx-auto px-8 py-20">
          <h2 className="font-display text-2xl font-semibold mb-12">Four ways to verify</h2>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-10">
            {inputs.map((item) => (
              <div key={item.label} className="border-l-2 border-signal/30 pl-5">
                <p className="font-mono-label text-xs uppercase text-signal mb-2">{item.label}</p>
                <p className="text-ink/70 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-ink text-white text-center py-20 px-8">
        <p className="font-mono-label text-xs uppercase text-signal mb-3">Get Started</p>
        <h2 className="font-display text-3xl font-semibold mb-8">Run your first scan, free.</h2>
        <button onClick={() => navigate("/signup")}
          className="bg-signal text-white px-8 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors">
          Create Account
        </button>
      </section>
    </div>
  );
}

export default LandingPage;