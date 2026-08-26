import { Link } from "react-router-dom";

const capabilities = [
  ["01", "Image intelligence", "Face-aware visual analysis with a lightweight CNN designed for fast product workflows."],
  ["02", "Video intelligence", "Frame-level evidence today, with a roadmap toward temporal and multimodal analysis."],
  ["03", "Audio intelligence", "Speech-focused spectrogram analysis for a second media signal beyond pixels."],
  ["04", "Live analysis", "Real-time webcam inference through a persistent WebSocket session."],
];

function LandingPage() {
  return (
    <main>
      <section className="landing-hero">
        <div className="landing-copy">
          <span className="eyebrow">AI MEDIA AUTHENTICITY PLATFORM</span>
          <h1>Trust what you see. <span>Verify what you watch.</span></h1>
          <p>Analyze images, videos and audio with an evolving deepfake detection platform built around face-aware inference, multiple signals, measurable evaluation and explicit uncertainty.</p>
          <div className="hero-actions">
            <Link className="hero-primary" to="/signup">Start an analysis</Link>
            <Link className="hero-secondary" to="/technology">Explore the technology →</Link>
          </div>
          <div className="hero-trust-row"><span>Visual AI</span><span>Audio AI</span><span>Live inference</span><span>Research-led</span></div>
        </div>
        <div className="hero-panel">
          <div className="panel-top"><span>AUTHENTICITY ENGINE</span><b>ONLINE</b></div>
          <div className="scan-orb"><span>AI</span></div>
          <div className="panel-score"><div><small>ANALYSIS MODES</small><strong>Image · Video · Audio</strong></div><div><small>VERDICT MODEL</small><strong>5 confidence bands</strong></div></div>
          <div className="signal-bars"><span style={{ width: "88%" }} /><span style={{ width: "68%" }} /><span style={{ width: "48%" }} /></div>
          <small className="panel-footnote">Signals are presented as model evidence, not as a guarantee of authenticity.</small>
        </div>
      </section>

      <section className="landing-section metrics-section">
        <div className="section-heading"><span className="eyebrow">DESIGNED AS A PLATFORM</span><h2>Built for analysis today, extensible for enterprise tomorrow.</h2><p>Start with a practical detection workflow and a transparent product surface. Expand toward APIs, collaboration, monitoring and higher-assurance multimodal detection as the underlying models mature.</p></div>
        <div className="capability-grid">{capabilities.map(([number,title,copy]) => <article className="capability-card" key={number}><b>{number}</b><h3>{title}</h3><p>{copy}</p></article>)}</div>
      </section>

      <section className="landing-section split-section">
        <div className="split-copy"><span className="eyebrow">WHY IT IS DIFFERENT</span><h2>Not every uncertain sample should be forced into “real” or “fake”.</h2><p>The product separates the raw model probability from its five-level user-facing confidence band. That makes ambiguity visible and creates room for better calibration, external validation and model improvements.</p><Link className="text-link" to="/research">Read the evaluation approach →</Link></div>
        <div className="signal-card"><div><span>OUTPUT</span><strong>REAL</strong><small>High confidence in authenticity</small></div><div><span>OUTPUT</span><strong>UNCERTAIN</strong><small>Evidence is not decisive</small></div><div><span>OUTPUT</span><strong>FAKE</strong><small>High confidence in manipulation</small></div></div>
      </section>

      <section className="landing-section dark-section">
        <div><span className="eyebrow">EXPLORE THE SYSTEM</span><h2>See the engine before you trust the result.</h2><p>Walk through preprocessing, model inference, signal analysis, validation and the limitations that matter when deploying deepfake detection in the real world.</p></div>
        <div className="hero-actions"><Link className="hero-secondary dark-link" to="/how-it-works">How it works →</Link><Link className="hero-secondary dark-link" to="/security">Security & privacy →</Link></div>
      </section>

      <section className="landing-cta"><div><span className="eyebrow">READY TO SHOWCASE THE PLATFORM?</span><h2>Turn media verification into a product your users can understand.</h2><p>Use the analysis workspace, research pages and live detection experience as the foundation for demos, pilots and future integrations.</p></div><Link className="hero-primary" to="/signup">Create your workspace →</Link></section>
    </main>
  );
}

export default LandingPage;
