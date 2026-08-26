function TechnologyPage() {
  const modules = [
    ["Image Detection", "Face-aware visual analysis using a transfer-learned CNN backbone."],
    ["Video Detection", "Frame-level evidence combined into a video-level authenticity assessment."],
    ["Audio Detection", "Spectrogram-based analysis for synthetic or manipulated speech."],
    ["rPPG Signal", "A supporting physiological-signal check used as an ensemble signal for video."],
    ["Live Detection", "Low-latency browser camera analysis through a persistent WebSocket connection."],
  ];

  return (
    <main className="site-page">
      <section className="page-hero">
        <span className="eyebrow">OUR TECHNOLOGY</span>
        <h1>Multiple signals. One authenticity decision.</h1>
        <p>Our platform combines visual, temporal, audio and physiological signals instead of treating every piece of media as a single black-box prediction.</p>
      </section>
      <section className="card-grid">
        {modules.map(([title, text]) => (
          <article className="info-card" key={title}>
            <span className="card-number">0{modules.findIndex((m) => m[0] === title) + 1}</span>
            <h2>{title}</h2>
            <p>{text}</p>
          </article>
        ))}
      </section>
      <section className="pipeline-card">
        <span className="eyebrow">ANALYSIS PIPELINE</span>
        <div className="pipeline">
          {['Input', 'Preprocess', 'Face / Signal Analysis', 'AI Models', 'Ensemble', 'Verdict'].map((step, i) => (
            <div className="pipeline-step" key={step}><b>{i + 1}</b><span>{step}</span></div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default TechnologyPage;
