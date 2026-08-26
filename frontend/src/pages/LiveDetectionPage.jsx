import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");

function LiveDetectionPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Starting camera…");
  const [error, setError] = useState("");

  useEffect(() => {
    let stream;
    let intervalId;
    let ws;
    let stopped = false;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
        if (stopped) return;
        videoRef.current.srcObject = stream;
        const token = localStorage.getItem("access_token");
        if (!token) throw new Error("Please sign in before starting live detection.");
        ws = new WebSocket(`${WS_BASE_URL}/live/webcam?token=${encodeURIComponent(token)}`);
        ws.onopen = () => setStatus("Live analysis active");
        ws.onclose = () => { if (!stopped) setStatus("Connection closed"); };
        ws.onerror = () => setStatus("Connection error");
        ws.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (payload.error) setError(payload.error);
            else { setError(""); setResult(payload); }
          } catch { setError("Received an invalid response from the analysis service."); }
        };

        intervalId = window.setInterval(() => {
          if (!ws || ws.readyState !== WebSocket.OPEN || !videoRef.current?.videoWidth) return;
          const canvas = canvasRef.current;
          const video = videoRef.current;
          canvas.width = 640;
          canvas.height = Math.round((video.videoHeight / video.videoWidth) * 640) || 360;
          canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
          ws.send(JSON.stringify({ image: canvas.toDataURL("image/jpeg", 0.68) }));
        }, 900);
      } catch (err) {
        setError(err.message || "Camera access could not be started.");
        setStatus("Unable to start");
      }
    }

    start();
    return () => {
      stopped = true;
      if (intervalId) clearInterval(intervalId);
      if (ws) ws.close();
      if (stream) stream.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const isFake = result?.label?.includes("Fake");
  const tone = isFake ? "danger" : result?.label === "REAL" ? "success" : "neutral";

  return (
    <main className="app-shell">
      <header className="page-app-head">
        <div><span className="eyebrow">REAL-TIME ANALYSIS</span><h1>Live detection.</h1><p>Stream camera frames to the visual detector and monitor the rolling verdict in real time.</p></div>
        <Link className="hero-secondary" to="/dashboard">Upload media instead →</Link>
      </header>
      {error && <div className="inline-error">{error}</div>}
      <section className="live-layout">
        <div className="live-card">
          <video ref={videoRef} autoPlay muted playsInline className="live-video" />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          <div className="live-body"><span className="live-status"><span className="status-dot" />{status}</span></div>
        </div>
        <div className="live-side">
          <div className="live-result">
            <span className="card-kicker">CURRENT VERDICT</span>
            {result?.label === "No Face" ? <strong className="live-verdict">No face</strong> : <strong className={`live-verdict ${tone}`}>{result?.label || "Waiting…"}</strong>}
            {result?.fake_percent != null && <><p style={{ color: "var(--muted)" }}>Real {result.real_percent}% · Fake {result.fake_percent}%</p><div className="meter"><span style={{ width: `${result.fake_percent}%` }} /></div></>}
            <small style={{ color: "#98a2b3" }}>Treat live output as model evidence, not proof of authenticity.</small>
          </div>
          <div className="live-help"><h3>How this session works</h3><p>The browser captures a low-bandwidth frame about once per second. The backend detects and aligns a face, runs the visual model, and returns the current confidence band.</p></div>
        </div>
      </section>
    </main>
  );
}

export default LiveDetectionPage;
