import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function DashboardPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFileChange(e) {
    const selected = e.target.files[0];
    if (!selected) return;

    let type = "image";
    if (selected.type.startsWith("video/")) type = "video";
    else if (selected.type.startsWith("audio/")) type = "audio";

    setFile(selected);
    setFileType(type);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setError("");
  }

  async function handleSubmit() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const endpointMap = { image: "/predict/image", video: "/predict/video", audio: "/predict/audio" };
      const response = await api.post(endpointMap[fileType], formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 402) {
        navigate("/upgrade");
        return;
      }
      setError(err.response?.data?.detail || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-lg mx-auto mt-12 px-6 text-center">
      <p className="font-mono-label text-xs uppercase text-signal mb-2">Scan a File</p>
      <h1 className="font-display text-3xl font-semibold mb-6">Check an Image, Video, or Audio Clip</h1>

      <input
        type="file"
        accept="image/*,video/*,audio/*"
        onChange={handleFileChange}
        className="block w-full text-sm border border-ink/20 rounded-sm p-2 mb-4"
      />

      {preview && fileType === "image" && (
        <img src={preview} alt="preview" className="rounded-sm max-h-72 mx-auto mb-4" />
      )}
      {preview && fileType === "video" && (
        <video src={preview} controls className="rounded-sm max-h-72 mx-auto mb-4" />
      )}
      {preview && fileType === "audio" && (
        <audio src={preview} controls className="w-full mb-4" />
      )}

      {file && (
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-signal text-white px-6 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors disabled:opacity-50"
        >
          {loading ? "Checking..." : "Check Now"}
        </button>
      )}

      {error && <p className="text-verdict-fake mt-4 text-sm">{error}</p>}

      {result && (
        <div
          className={`mt-6 p-6 rounded-sm border-l-4 bg-white text-left ${
            result.label === "REAL" || result.label === "Possibly Real"
              ? "border-verdict-real"
              : result.label === "FAKE" || result.label === "Possibly Fake"
              ? "border-verdict-fake"
              : "border-verdict-uncertain"
          }`}
        >
          <p className="font-mono-label text-xs uppercase text-ink/40 mb-1">Verdict</p>
          <h2 className="font-display text-2xl font-semibold mb-3">{result.label}</h2>
          <div className="h-1.5 w-full bg-ink/10 rounded-full overflow-hidden mb-2">
            <div className="h-full bg-verdict-fake" style={{ width: `${result.fake_percent}%` }} />
          </div>
          <p className="font-mono-label text-xs text-ink/50">
            REAL {result.real_percent}% — FAKE {result.fake_percent}%
          </p>
          {result.frames_analyzed !== undefined && (
            <p className="font-mono-label text-[11px] text-ink/30 mt-2">
              {result.frames_analyzed} FRAMES ANALYZED
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default DashboardPage;