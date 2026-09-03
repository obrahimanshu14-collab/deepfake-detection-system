import { useNavigate } from "react-router-dom";

function LandingPage() {
  const navigate = useNavigate();

  const deepfakeTypes = [
    { title: "Face Swaps", desc: "One person's face is digitally placed onto another person's body in a photo or video — often used to fabricate footage of someone saying or doing something they never did." },
    { title: "Voice Cloning", desc: "AI recreates a person's voice from just a few seconds of audio, used increasingly in phone scams impersonating family members, executives, or public figures." },
    { title: "Fully Synthetic Faces", desc: "Entire faces generated from scratch by AI — no real person behind them at all, often used for fake profiles and social engineering." },
    { title: "AI Avatars", desc: "A real person's likeness animated to say new things via AI, blurring the line between a genuine recording and a fabricated one." },
  ];

  const useCases = [
    { title: "Individuals", desc: "Verify a suspicious video call, a voice message that doesn't feel right, or a photo circulating on social media before you trust or share it." },
    { title: "Journalists & Fact-Checkers", desc: "Screen user-submitted footage and viral content for signs of manipulation before publication." },
    { title: "Businesses", desc: "Add a verification layer to identity checks, video onboarding, or customer support calls to reduce fraud." },
    { title: "Families", desc: "Protect against voice-cloning scams targeting elderly relatives with fabricated emergency calls." },
  ];

  const steps = [
    { n: "1", title: "Upload or Connect", desc: "Submit a photo, video, or audio clip — or turn on your webcam for a live check." },
    { n: "2", title: "We Examine It", desc: "Our system looks for the subtle signs that AI-generated content leaves behind — things invisible to the naked eye." },
    { n: "3", title: "Get a Clear Answer", desc: "Instead of a vague yes or no, you get a confidence score and a plain-language verdict you can actually act on." },
  ];

  return (
    <div>
      {/* Hero */}
      <section className="max-w-6xl mx-auto px-8 pt-20 pb-16 grid md:grid-cols-2 gap-16 items-center">
        <div>
          <p className="font-mono-label text-xs uppercase text-signal mb-4">AI Content Verification</p>
          <h1 className="font-display text-5xl font-semibold leading-tight mb-6">
            Is it real?<br />Now you can check.
          </h1>
          <p className="text-lg text-ink/70 leading-relaxed mb-8 max-w-md">
            Veritas checks photos, videos, voice recordings, and live video calls
            for signs of AI manipulation — and gives you a clear, honest answer
            instead of a guess.
          </p>
          <div className="flex gap-4">
            <button onClick={() => navigate("/signup")}
              className="bg-signal text-white px-7 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors">
              Try It Free
            </button>
            <button onClick={() => navigate("/login")}
              className="border border-ink/20 px-7 py-3 rounded-sm font-medium hover:border-signal transition-colors">
              Login
            </button>
          </div>
          <p className="text-xs text-ink/40 mt-4">No credit card required · 5 free checks</p>
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
            <span className="font-mono-label text-[11px] uppercase text-ink/40">Example result</span>
            <span className="font-mono-label text-[11px] uppercase text-verdict-real">Real — 96.2%</span>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-t border-b border-ink/10 bg-white py-10">
        <div className="max-w-6xl mx-auto px-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div>
            <p className="font-display text-3xl font-semibold text-signal">4</p>
            <p className="text-xs uppercase text-ink/40 mt-1 tracking-wide">Ways to Verify</p>
          </div>
          <div>
            <p className="font-display text-3xl font-semibold text-signal">5</p>
            <p className="text-xs uppercase text-ink/40 mt-1 tracking-wide">Free Checks</p>
          </div>
          <div>
            <p className="font-display text-3xl font-semibold text-signal">Instant</p>
            <p className="text-xs uppercase text-ink/40 mt-1 tracking-wide">Results</p>
          </div>
          <div>
            <p className="font-display text-3xl font-semibold text-signal">24/7</p>
            <p className="text-xs uppercase text-ink/40 mt-1 tracking-wide">Availability</p>
          </div>
        </div>
      </section>

      {/* What is a deepfake — educational */}
      <section className="max-w-6xl mx-auto px-8 py-20">
        <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">Understanding the Threat</p>
        <h2 className="font-display text-3xl font-semibold text-center mb-4">What exactly is a deepfake?</h2>
        <p className="text-ink/60 text-center max-w-2xl mx-auto mb-14 leading-relaxed">
          "Deepfake" describes any photo, video, or audio clip created or
          altered by AI to make it look or sound real when it isn't. The
          technology has become cheap, fast, and convincing — and it comes
          in several different forms.
        </p>
        <div className="grid md:grid-cols-2 gap-x-12 gap-y-10">
          {deepfakeTypes.map((item) => (
            <div key={item.title} className="border-l-2 border-signal/30 pl-5">
              <p className="font-semibold text-lg mb-2">{item.title}</p>
              <p className="text-ink/60 leading-relaxed text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Why it matters */}
      <section className="bg-white border-t border-ink/10 py-20">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <p className="font-mono-label text-xs uppercase text-signal mb-2">Why It Matters</p>
          <h2 className="font-display text-3xl font-semibold mb-6">This isn't a hypothetical risk</h2>
          <p className="text-ink/70 leading-relaxed mb-4">
            Deepfakes are already being used in phone scams that clone a
            loved one's voice to fake an emergency, in fraudulent video
            calls used to bypass identity checks, and in fabricated clips
            spread to damage reputations or mislead the public.
          </p>
          <p className="text-ink/70 leading-relaxed">
            As the technology improves, telling real from fake with the
            naked eye is only getting harder — which is exactly the gap
            Veritas is built to close.
          </p>
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-6xl mx-auto px-8 py-20">
        <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">Simple By Design</p>
        <h2 className="font-display text-3xl font-semibold text-center mb-14">How Veritas works</h2>
        <div className="grid md:grid-cols-3 gap-10">
          {steps.map((s) => (
            <div key={s.n} className="text-center">
              <div className="w-12 h-12 rounded-full bg-signal text-white flex items-center justify-center font-display text-lg font-semibold mx-auto mb-4">
                {s.n}
              </div>
              <p className="font-semibold text-lg mb-2">{s.title}</p>
              <p className="text-ink/60 text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="bg-white border-t border-ink/10 py-20">
        <div className="max-w-6xl mx-auto px-8">
          <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">What You Can Check</p>
          <h2 className="font-display text-3xl font-semibold text-center mb-14">Four ways to verify</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="border border-ink/10 rounded-sm p-6 hover:shadow-md transition">
              <p className="font-semibold mb-2">Photos</p>
              <p className="text-sm text-ink/60 leading-relaxed">Upload any image and find out if a face was digitally generated or altered.</p>
            </div>
            <div className="border border-ink/10 rounded-sm p-6 hover:shadow-md transition">
              <p className="font-semibold mb-2">Videos</p>
              <p className="text-sm text-ink/60 leading-relaxed">We examine footage frame by frame, plus signs of natural human movement that AI struggles to fake.</p>
            </div>
            <div className="border border-ink/10 rounded-sm p-6 hover:shadow-md transition">
              <p className="font-semibold mb-2">Voice & Audio</p>
              <p className="text-sm text-ink/60 leading-relaxed">Detect cloned or synthetically generated speech, even from short clips.</p>
            </div>
            <div className="border border-ink/10 rounded-sm p-6 hover:shadow-md transition">
              <p className="font-semibold mb-2">Live Video Calls</p>
              <p className="text-sm text-ink/60 leading-relaxed">Turn on your webcam for a running, real-time check during a live call.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use cases */}
      <section className="max-w-6xl mx-auto px-8 py-20">
        <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">Built For Everyone</p>
        <h2 className="font-display text-3xl font-semibold text-center mb-14">Who uses Veritas</h2>
        <div className="grid md:grid-cols-2 gap-x-12 gap-y-10">
          {useCases.map((item) => (
            <div key={item.title} className="flex gap-4">
              <div className="w-1 bg-signal/30 rounded-full flex-shrink-0" />
              <div>
                <p className="font-semibold text-lg mb-2">{item.title}</p>
                <p className="text-ink/60 leading-relaxed text-sm">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Why choose us */}
      <section className="bg-white border-t border-ink/10 py-20">
        <div className="max-w-4xl mx-auto px-8">
          <p className="font-mono-label text-xs uppercase text-signal mb-2 text-center">Our Approach</p>
          <h2 className="font-display text-3xl font-semibold text-center mb-14">Honesty over false confidence</h2>
          <div className="space-y-8">
            <div className="flex gap-4">
              <span className="text-signal font-display text-2xl">01</span>
              <div>
                <p className="font-semibold mb-1">No fake certainty</p>
                <p className="text-ink/60 text-sm leading-relaxed">No detector is ever 100% certain. We show you a confidence score instead of pretending otherwise — including "uncertain" when that's the honest answer.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-signal font-display text-2xl">02</span>
              <div>
                <p className="font-semibold mb-1">Multiple checks, one answer</p>
                <p className="text-ink/60 text-sm leading-relaxed">For video, we don't rely on a single method — several independent checks are combined into one final result.</p>
              </div>
            </div>
            <div className="flex gap-4">
              <span className="text-signal font-display text-2xl">03</span>
              <div>
                <p className="font-semibold mb-1">Your data stays yours</p>
                <p className="text-ink/60 text-sm leading-relaxed">Files are stored in your account so you can revisit results from History. Production deployments should use durable private object storage for long-term retention.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-ink text-white text-center py-24 px-8">
        <p className="font-mono-label text-xs uppercase text-signal mb-3">Get Started</p>
        <h2 className="font-display text-3xl font-semibold mb-4">Stop guessing. Start verifying.</h2>
        <p className="text-white/50 max-w-md mx-auto mb-8">
          Create a free account and run your first check in under a minute.
        </p>
        <button onClick={() => navigate("/signup")}
          className="bg-signal text-white px-8 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors">
          Create Free Account
        </button>
      </section>
    </div>
  );
}

export default LandingPage;