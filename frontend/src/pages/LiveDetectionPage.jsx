import { useEffect, useRef, useState } from "react";
import api, { API_BASE_URL } from "../services/api";

const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");

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
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const sessionStartRef = useRef(null);
  const summaryRef = useRef(null);

  const [status, setStatus] = useState("Idle");
  const [liveResult, setLiveResult] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [saving, setSaving] = useState(false);

  async function startSession() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("Camera unavailable in this browser");
      return;
    }
    setSessionSummary(null);
    fakePercentsRef.current = [];
    recordedChunksRef.current = [];
    sessionStartRef.current = Date.now();
    setStatus("Requesting camera...");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      const mimeType = MediaRecorder.isTypeSupported("video/webm;codecs=vp9,opus")
        ? "video/webm;codecs=vp9,opus"
        : "video/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) recordedChunksRef.current.push(event.data);
      };
      recorder.onstop = handleRecordingStopped;
      recorder.start(1000);
      mediaRecorderRef.current = recorder;

      const token = localStorage.getItem("access_token");
      const ws = new WebSocket(`${WS_BASE_URL}/live/webcam?token=${encodeURIComponent(token)}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("Live");
        setIsRunning(true);
      };
      ws.onclose = () => {
        if (isRunning) setStatus("Disconnected");
      };
      ws.onerror = () => setStatus("Connection error");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.error) {
          setStatus(data.error);
          return;
        }
        setLiveResult(data);
        if (typeof data.fake_percent === "number") fakePercentsRef.current.push(data.fake_percent);
      };

      intervalRef.current = setInterval(() => {
        if (ws.readyState !== WebSocket.OPEN) return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        if (!video?.videoWidth || !video?.videoHeight) return;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        ws.send(JSON.stringify({ image: canvas.toDataURL("image/jpeg", 0.8) }));
      }, 1000);
    } catch (error) {
      setIsRunning(false);
      setStatus("Camera permission or live connection failed");
      if (error?.name === "NotAllowedError") setStatus("Camera permission was denied");
    }
  }

  function stopSession() {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = null;
    if (wsRef.current) wsRef.current.close();
    const samples = fakePercentsRef.current;
    const durationSeconds = sessionStartRef.current ? (Date.now() - sessionStartRef.current) / 1000 : 0;
    if (samples.length) {
      const avg = samples.reduce((a, b) => a + b, 0) / samples.length;
      summaryRef.current = {
        label: classifySessionLabel(avg),
        realPercent: (100 - avg).toFixed(1),
        fakePercent: avg.toFixed(1),
        framesAnalyzed: samples.length,
        durationSeconds,
      };
    } else {
      summaryRef.current = { label: "No Data", note: "No usable face frames were returned during the session.", durationSeconds };
    }
    setIsRunning(false);
    setStatus("Idle");
    setLiveResult(null);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") mediaRecorderRef.current.stop();
    else handleRecordingStopped();
  }

  async function handleRecordingStopped() {
    if (streamRef.current) streamRef.current.getTracks().forEach((track) => track.stop());
    const summary = summaryRef.current;
    setSessionSummary(summary);
    if (!summary || summary.label === "No Data" || !recordedChunksRef.current.length) return;
    setSaving(true);
    try {
      const blob = new Blob(recordedChunksRef.current, { type: "video/webm" });
      const formData = new FormData();
      formData.append("file", blob, "live-session.webm");
      formData.append("label", summary.label);
      formData.append("real_percent", summary.realPercent);
      formData.append("fake_percent", summary.fakePercent);
      formData.append("duration_seconds", summary.durationSeconds);
      await api.post("/predict/live/save", formData);
    } catch {
      // The on-screen result remains useful even when history storage fails.
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (wsRef.current) wsRef.current.close();
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") mediaRecorderRef.current.stop();
    if (streamRef.current) streamRef.current.getTracks().forEach((track) => track.stop());
  }, []);

  const labelColor = {
    REAL: "text-verdict-real", "Possibly Real": "text-verdict-real",
    Uncertain: "text-verdict-uncertain", "Possibly Fake": "text-verdict-fake", FAKE: "text-verdict-fake",
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 px-6 pb-16">
      <div className="text-center mb-8">
        <p className="font-mono-label text-xs uppercase text-signal mb-2">Real-time analysis</p>
        <h1 className="font-display text-3xl font-semibold mb-2">Live Detection</h1>
        <p className="text-sm text-ink/50">Camera frames are checked locally in the browser pipeline and analyzed by the live inference API.</p>
      </div>
      <div className="grid lg:grid-cols-[1.7fr_1fr] gap-8 items-start">
        <div>
          <div className="relative rounded-sm overflow-hidden border border-ink/10 bg-black shadow-sm aspect-video">
            <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover" />
            {!isRunning && <div className="absolute inset-0 grid place-items-center text-white/70 text-sm">Start the session to activate your camera.</div>}
            {isRunning && liveResult && <div className="absolute top-3 left-3 bg-black/70 text-white text-sm px-3 py-1.5 rounded-sm">{liveResult.label} — {liveResult.fake_percent ?? "—"}% fake</div>}
          </div>
          <canvas ref={canvasRef} className="hidden" />
          <div className="flex items-center justify-between mt-4">
            <span className="text-xs uppercase tracking-widest text-ink/40">Status: {status}</span>
            {!isRunning ? (
              <button onClick={startSession} className="bg-signal text-white px-6 py-3 rounded-sm font-medium hover:bg-signal-dark">Start Live Detection</button>
            ) : (
              <button onClick={stopSession} className="bg-verdict-fake text-white px-6 py-3 rounded-sm font-medium hover:opacity-90">Stop &amp; Get Verdict</button>
            )}
          </div>
        </div>
        <aside className="border border-ink/10 rounded-sm p-6 bg-white">
          <p className="font-mono-label text-xs uppercase text-signal mb-3">How to use</p>
          <div className="space-y-4 text-sm text-ink/60">
            <p><strong className="text-ink">01</strong> Allow camera access.</p>
            <p><strong className="text-ink">02</strong> Keep one face centered and well lit.</p>
            <p><strong className="text-ink">03</strong> Let it sample for a few seconds before stopping.</p>
          </div>
          <p className="text-xs text-ink/40 mt-6 leading-relaxed">Live results are indicative signals, not a guarantee of authenticity.</p>
        </aside>
      </div>

      {sessionSummary && (
        <div className="mt-8 p-6 border border-ink/10 rounded-sm bg-white">
          <p className="font-mono-label text-xs uppercase text-ink/40 mb-1">Session Summary</p>
          {sessionSummary.note ? <p className="text-ink/60">{sessionSummary.note}</p> : (
            <>
              <h3 className={`font-display text-2xl font-semibold ${labelColor[sessionSummary.label] || ""}`}>{sessionSummary.label}</h3>
              <p className="text-ink/60 mt-1">Real: {sessionSummary.realPercent}% · Fake: {sessionSummary.fakePercent}%</p>
              <p className="text-xs text-ink/40 mt-1">{sessionSummary.framesAnalyzed} samples analyzed over {Math.round(sessionSummary.durationSeconds)}s</p>
              {saving && <p className="text-xs text-signal mt-2">Saving to history…</p>}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default LiveDetectionPage;
