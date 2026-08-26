function SecurityPage() {
  const items = [
    ["Authentication", "Protected analysis and history endpoints require an authenticated user."],
    ["Configuration", "JWT secrets, database credentials and frontend origins are kept outside source code."],
    ["Upload handling", "Media is processed through temporary files rather than being permanently stored by the prediction endpoint."],
    ["Privacy by design", "Production deployment should add explicit retention, deletion and privacy controls before handling sensitive media."],
  ];

  return (
    <main className="site-page">
      <section className="page-hero"><span className="eyebrow">SECURITY & PRIVACY</span><h1>Designed to protect the analysis pipeline.</h1><p>Security is part of the product architecture, not a final checkbox.</p></section>
      <section className="card-grid">{items.map(([title, text]) => <article className="info-card" key={title}><h2>{title}</h2><p>{text}</p></article>)}</section>
      <section className="notice-card"><strong>Production note</strong><p>Before public deployment, the project will also receive upload limits, MIME validation, rate limiting, HTTPS/WSS configuration and stronger operational logging.</p></section>
    </main>
  );
}

export default SecurityPage;
