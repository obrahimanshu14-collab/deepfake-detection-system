import { Link } from "react-router-dom";

function LandingPage() {
  return (
    <main>
      <section className="landing-hero">
        <div className="landing-copy">
          <span className="eyebrow">AI MEDIA AUTHENTICITY PLATFORM</span>
          <h1>Trust what you see. <span>Verify what you watch.</span></h1>
          <p>Analyze images, videos and audio with an AI-powered deepfake detection system built around multiple signals, measurable evaluation and transparent limitations.</p>
          <div className="hero-actions">
            <Link className="hero-primary" to="/signup">Start an analysis</Link>
            <Link className="hero-secondary" to="/technology">Explore the technology →</Link>
          </div>
        </div>
        <div className="hero-panel">
          <div className="panel-top"><span>AUTHENTICITY ANALYSIS</span><b>LIVE</b></div>
          <div className="scan-orb"><span>AI</span></div>
          <div className="panel-score"><div><small>ANALYSIS ENGINE</small><strong>Multi-signal</strong></div><div><small>MEDIA TYPES</small><strong>Image · Video · Audio</strong></div></div>
          <div className="signal-bars"><span style={{ width: "88%" }} /><span style={{ width: "68%" }} /><span style={{ width: "48%" }} /></div>
        </div>
      </section>

      <section className="landing-section">
        <div className="section-heading"><span className="eyebrow">BUILT FOR REAL-WORLD MEDIA</span><h2>One platform. Multiple detection layers.</h2></div>
        <div className="feature-grid">
          <article><b>01</b><h3>Visual analysis</h3><p>Face-aware image and video analysis with a dedicated CNN pipeline.</p></article>
          <article><b>02</b><h3>Signal analysis</h3><p>Audio and rPPG signals provide additional evidence beyond a single frame.</p></article>
          <article><b>03</b><h3>Transparent evaluation</h3><p>Held-out testing, robustness experiments and external validation expose model weaknesses.</p></article>
        </div>
      </section>

      <section className="landing-section dark-section">
        <div><span className="eyebrow">SEE THE SYSTEM</span><h2>Understand the decision, not just the label.</h2><p>Explore how preprocessing, model inference, ensemble signals and the final verdict connect.</p></div>
        <Link className="hero-secondary dark-link" to="/how-it-works">See how it works →</Link>
      </section>
    </main>
  );
}

export default LandingPage;
