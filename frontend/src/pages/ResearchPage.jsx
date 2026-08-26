function ResearchPage() {
  const areas = [
    ["Evaluation", "Accuracy alone is not enough. We track precision, recall, F1, ROC-AUC and confusion matrices on held-out data."],
    ["Robustness", "Resolution, compression, blur, noise and other real-world transformations are treated as explicit evaluation conditions."],
    ["External Validation", "The system is intended to be evaluated on media outside the training distribution to measure generalization."],
    ["Known Limitations", "Talking-avatar and highly novel manipulation techniques can expose gaps in frame-level CNN detection; these are tracked rather than hidden."],
  ];

  return (
    <main className="site-page">
      <section className="page-hero">
        <span className="eyebrow">RESEARCH & EVALUATION</span>
        <h1>Measure what the model gets wrong.</h1>
        <p>Our evaluation layer is designed to expose weaknesses, not just display a high headline accuracy.</p>
      </section>
      <section className="card-grid">
        {areas.map(([title, text]) => <article className="info-card" key={title}><h2>{title}</h2><p>{text}</p></article>)}
      </section>
      <section className="notice-card"><strong>Baseline status</strong><p>The current development branch now records held-out test metrics separately from validation-based model selection. This keeps the final test set out of training decisions.</p></section>
    </main>
  );
}

export default ResearchPage;
