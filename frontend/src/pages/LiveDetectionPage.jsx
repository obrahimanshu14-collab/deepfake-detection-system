import { useEffect, useRef, useState } from "react";

const WS_BASE_URL = "ws://127.0.0.1:8000";

function LiveDetectionPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Connecting...");

  useEffect(() => {
    let stream;
    let intervalId;
    let ws;

    async function start() {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;

      const token = localStorage.getItem("access_token");
      ws = new WebSocket(`${WS_BASE_URL}/live/webcam?token=${token}`);

      ws.onopen = () => setStatus("Live");
      ws.onclose = () => setStatus("Disconnected");
      ws.onerror = () => setStatus("Connection error");
      ws.onmessage = (event) => setResult(JSON.parse(event.data));

      intervalId = setInterval(() => {
        if (ws.readyState !== WebSocket.OPEN) return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.7);
        ws.send(JSON.stringify({ image: dataUrl }));
      }, 1000);
    }

    start();

    return () => {
      if (intervalId) clearInterval(intervalId);
      if (ws) ws.close();
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h1>Live Detection</h1>
      <p>Status: {status}</p>
      <video ref={videoRef} autoPlay muted style={{ maxWidth: "480px", borderRadius: "8px" }} />
      <canvas ref={canvasRef} style={{ display: "none" }} />
      {result && (
        <div style={{ marginTop: "20px" }}>
          {result.label === "No Face" ? (
            <p>No face detected</p>
          ) : (
            <>
              <h2>{result.label}</h2>
              <p>Real: {result.real_percent}% | Fake: {result.fake_percent}%</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default LiveDetectionPage;