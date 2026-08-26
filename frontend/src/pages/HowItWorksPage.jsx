function HowItWorksPage() {
  const steps = [
    ["01", "Upload", "Choose an image, video or audio file for analysis."],
    ["02", "Preprocess", "The system prepares the media and extracts the relevant face, frame or audio representation."],
    ["03", "Analyze", "Specialized models inspect visual and signal-level evidence."],
    ["04", "Combine", "Available signals are combined into a calibrated authenticity score."],
    ["05", "Explain", "The interface presents the verdict, confidence and supporting analysis signals."],
  ];

  return (
    <main className="site-page">
      <section className="page-hero"><span className="eyebrow">HOW IT WORKS</span><h1>From media upload to an evidence-backed verdict.</h1><p>Explore the complete path a file takes through the detection system.</p></section>
      <section className="steps-list">
        {steps.map(([number, title, text]) => <article className="step-row" key={number}><span>{number}</span><div><h2>{title}</h2><p>{text}</p></div></article>)}
      </section>
    </main>
  );
}

export default HowItWorksPage;
