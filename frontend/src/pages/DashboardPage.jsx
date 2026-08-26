import { useEffect, useRef, useState } from "react";
import api from "../services/api";

const ACCEPTED = {
  image: ["image/jpeg", "image/png", "image/webp"],
  video: ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"],
  audio: ["audio/wav", "audio/mpeg", "audio/mp4", "audio/flac", "audio/ogg"],
};

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function DashboardPage() {
  const inputRef = useRef(null);
  const previewUrlRef = useRef(null);
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => () => {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
  }, []);

  function chooseFile(selected) {
    if (!selected) return;
    const detectedType = selected.type.startsWith("video/")
      ? "video"
      : selected.type.startsWith("audio/")
        ? "audio"
        : "image";

    if (!ACCEPTED[detectedType].includes(selected.type)) {
      setError("This file type is not supported. Please use a supported image, video or audio format.");
      return;
    }
    if (selected.size > 200 * 1024 * 1024) {
      setError("File is larger than the 200 MB application limit.");
      return;
    }

    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    const url = URL.createObjectURL(selected);
    previewUrlRef.current = url;
    setFile(selected);
    setFileType(detectedType);
    setPreview(url);
    setResult(null);
    setError("");
  }

  function handleFileChange(event) {
    chooseFile(event.target.files?.[0]);
  }

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files?.[0]);
  }

  async function handleSubmit() {
    if (!file || !fileType) return;
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const endpoint = { image: "/predict/image", video: "/predict/video", audio: "/predict/audio" }[fileType];
      const response = await api.post(endpoint, formData, { headers: { "Content-Type": "multipart/form-data" } });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function clearSelection() {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    previewUrlRef.current = null;
    setFile(null);
    setFileType(null);
    setPreview(null);
    setResult(null);
    setError("");
    if (inputRef.current) inputRef.current.value = "";
  }

  const fakeProbability = result?.fake_percent != null ? Number(result.fake_percent) : null;
  const verdictTone = result?.label?.toLowerCase().includes("fake") ? "danger" : result?.label === "REAL" ? "success" : "neutral";

  return (
    <main className="app-shell">
      <section className="workspace-head">
        <div>
          <span className="eyebrow">AUTHENTICITY WORKSPACE</span>
          <h1>Analyze media with context, not just a label.</h1>
          <p>Upload an image, video or audio sample. The system returns a confidence-based verdict and the signals available for that analysis.</p>
        </div>
        <div className="workspace-badge"><span className="status-dot" /> Detection engine online</div>
      </section>

      <section className="workspace-grid">
        <div className="analysis-card">
          <div className="card-heading">
            <div><span className="card-kicker">NEW ANALYSIS</span><h2>Choose a media sample</h2></div>
            {file && <button className="text-button" onClick={clearSelection}>Clear</button>}
          </div>

          <div
            className={`drop-zone ${dragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input ref={inputRef} type="file" hidden accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/x-msvideo,video/webm,audio/wav,audio/mpeg,audio/mp4,audio/flac,audio/ogg" onChange={handleFileChange} />
            <div className="drop-icon">↑</div>
            <strong>{file ? "Replace this sample" : "Drop a file here or browse"}</strong>
            <span>Images · Videos · Audio</span>
            <small>Up to 200 MB for media analysis. Supported formats are validated before processing.</small>
          </div>

          {file && (
            <div className="selected-file">
              <div><span className="file-chip">{fileType?.toUpperCase()}</span><strong>{file.name}</strong><small>{formatBytes(file.size)}</small></div>
              <button className="primary-button" onClick={handleSubmit} disabled={loading}>{loading ? "Analyzing…" : "Run analysis"}</button>
            </div>
          )}

          {preview && (
            <div className="preview-card">
              <div className="preview-head"><span>INPUT PREVIEW</span><small>Original sample</small></div>
              {fileType === "image" && <img src={preview} alt="Selected media preview" />}
              {fileType === "video" && <video src={preview} controls />}
              {fileType === "audio" && <audio src={preview} controls />}
            </div>
          )}

          {error && <div className="inline-error">{error}</div>}
        </div>

        <aside className="result-card">
          <div className="card-heading"><div><span className="card-kicker">RESULT</span><h2>{result ? "Analysis complete" : "Your result appears here"}</h2></div></div>
          {!result ? (
            <div className="empty-result">
              <div className="result-orb">AI</div>
              <p>Run an analysis to see the verdict, probability and available supporting signals.</p>
            </div>
          ) : (
            <div className="result-content">
              <div className={`verdict-banner ${verdictTone}`}>
                <span>VERDICT</span><strong>{result.label}</strong><small>{fakeProbability != null ? `${fakeProbability.toFixed(1)}% estimated fake probability` : ""}</small>
              </div>
              <div className="probability-grid">
                <div><span>Real</span><strong>{result.real_percent}%</strong></div>
                <div><span>Fake</span><strong>{result.fake_percent}%</strong></div>
              </div>
              {fakeProbability != null && <div className="meter"><span style={{ width: `${Math.min(Math.max(fakeProbability, 0), 100)}%` }} /></div>}
              {result.frames_analyzed !== undefined && <div className="metric-row"><span>Frames analyzed</span><strong>{result.frames_analyzed}</strong></div>}
              <div className="trust-note"><strong>How to read this</strong><p>The probability is an AI model output, not proof of authenticity. Use the confidence band and additional context when making decisions.</p></div>
            </div>
          )}
        </aside>
      </section>

      <section className="workspace-info-grid">
        <article><span>01</span><h3>Visual evidence</h3><p>Face-aware image and video analysis using the trained visual detector.</p></article>
        <article><span>02</span><h3>Multiple signals</h3><p>Video analysis can combine CNN evidence with the current rPPG signal layer.</p></article>
        <article><span>03</span><h3>Transparent uncertainty</h3><p>The five-level verdict avoids pretending that every ambiguous sample is certainly real or fake.</p></article>
      </section>
    </main>
  );
}

export default DashboardPage;
