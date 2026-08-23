import { useEffect, useRef, useState } from "react";

const WS_BASE_URL = "ws://127.0.0.1:8000";

function classifySessionLabel(avgFakePercent) {
  if (avgFakePercent < 15) return "REAL";
  if (avgFakePercent < 40) return "Possibly Real";
  if (avgFakePercent < 60) return "Uncertain";
  if (avgFakePercent < 85) return "Possibly Fake";
  return "FAKE";
}

function LiveDetectionPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const fakePercentsRef = useRef([]);

  const [status, setStatus] = useState("Idle");
  const [liveResult, setLiveResult] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  async function startSession() {
    setSessionSummary(null);
    fakePercentsRef.current = [];
    setStatus("Connecting...");
    setIsRunning(true);

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    streamRef.current = stream;
    videoRef.current.srcObject = stream;

    const token = localStorage.getItem("access_token");
    const ws = new WebSocket(`${WS_BASE_URL}/live/webcam?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => setStatus("Live");
    ws.onclose = () => setStatus("Disconnected");
    ws.onerror = () => setStatus("Connection error");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLiveResult(data);
      if (typeof data.fake_percent === "number") {
        fakePercentsRef.current.push(data.fake_percent);
      }
    };

    intervalRef.current = setInterval(() => {
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

  function stopSession() {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (wsRef.current) wsRef.current.close();
    if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());

    const samples = fakePercentsRef.current;
    if (samples.length > 0) {
      const avg = samples.reduce((a, b) => a + b, 0) / samples.length;
      setSessionSummary({
        label: classifySessionLabel(avg),
        realPercent: (100 - avg).toFixed(1),
        fakePercent: avg.toFixed(1),
        framesAnalyzed: samples.length,
      });
    } else {
      setSessionSummary({ label: "No Data", note: "No face was detected during the session." });
    }

    setIsRunning(false);
    setStatus("Idle");
    setLiveResult(null);
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (wsRef.current) wsRef.current.close();
      if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const labelColor = {
    REAL: "text-green-600", "Possibly Real": "text-green-500",
    Uncertain: "text-gray-500", "Possibly Fake": "text-orange-500", FAKE: "text-red-600",
  };

  return (
    <div className="max-w-xl mx-auto mt-10 px-6 text-center">
      <h1 className="text-3xl font-bold mb-2">Live Detection</h1>
      <p className="text-sm text-gray-500 mb-6">
        Status: <span className="font-medium">{status}</span>
      </p>

      <div className="relative rounded-xl overflow-hidden border shadow-sm">
        <video ref={videoRef} autoPlay muted className="w-full" />
        {isRunning && liveResult && liveResult.label !== "No Face" && (
          <div className="absolute top-3 left-3 bg-black/60 text-white text-sm px-3 py-1.5 rounded-lg">
            {liveResult.label} — {liveResult.fake_percent}% fake
          </div>
        )}
        {isRunning && liveResult && liveResult.label === "No Face" && (
          <div className="absolute top-3 left-3 bg-black/60 text-white text-sm px-3 py-1.5 rounded-lg">
            No face detected
          </div>
        )}
      </div>
      <canvas ref={canvasRef} className="hidden" />

      <div className="mt-5">
        {!isRunning ? (
          <button
            onClick={startSession}
            className="bg-brand-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-brand-700"
          >
            Start Live Detection
          </button>
        ) : (
          <button
            onClick={stopSession}
            className="bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700"
          >
            Stop &amp; Get Final Verdict
          </button>
        )}
      </div>

      {sessionSummary && (
        <div className="mt-6 p-6 border rounded-xl shadow-sm text-left">
          <h2 className="text-sm text-gray-500 mb-1">Session Summary</h2>
          {sessionSummary.note ? (
            <p className="text-gray-600">{sessionSummary.note}</p>
          ) : (
            <>
              <h3 className={`text-2xl font-bold ${labelColor[sessionSummary.label] || ""}`}>
                {sessionSummary.label}
              </h3>
              <p className="text-gray-600 mt-1">
                Real: {sessionSummary.realPercent}% | Fake: {sessionSummary.fakePercent}%
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Based on {sessionSummary.framesAnalyzed} analyzed frames
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default LiveDetectionPage;