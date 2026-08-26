import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-main">
        <div className="footer-brand">
          <Link to="/" className="brand-mark"><span className="brand-icon">D</span><span>Deepfake Detector</span></Link>
          <p>AI-powered media authenticity analysis for images, videos, audio and live sessions.</p>
        </div>
        <div className="footer-links">
          <div><span>PRODUCT</span><Link to="/dashboard">Analyze</Link><Link to="/live">Live detection</Link><Link to="/history">History</Link></div>
          <div><span>LEARN</span><Link to="/technology">Technology</Link><Link to="/how-it-works">How it works</Link><Link to="/research">Research</Link></div>
          <div><span>TRUST</span><Link to="/security">Security</Link><Link to="/signup">Get started</Link></div>
        </div>
      </div>
      <div className="footer-bottom"><span>© {new Date().getFullYear()} Deepfake Detector</span><span>Built as an evolving research and product platform.</span></div>
    </footer>
  );
}

export default Footer;
