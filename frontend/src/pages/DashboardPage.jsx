import { useState } from "react";
import api from "../services/api";

function DashboardPage() {
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
      setError(err.response?.data?.detail || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <h1>Check an Image, Video, or Audio Clip</h1>
      <input type="file" accept="image/*,video/*,audio/*" onChange={handleFileChange} />

      {preview && fileType === "image" && <img src={preview} alt="preview" style={styles.preview} />}
      {preview && fileType === "video" && <video src={preview} controls style={styles.preview} />}
      {preview && fileType === "audio" && <audio src={preview} controls style={{ marginTop: "20px" }} />}

      {file && (
        <button style={styles.button} onClick={handleSubmit} disabled={loading}>
          {loading ? "Checking..." : "Check Now"}
        </button>
      )}

      {error && <p style={styles.error}>{error}</p>}

      {result && (
        <div style={styles.resultBox}>
          <h2>{result.label}</h2>
          <p>Real: {result.real_percent}% &nbsp;|&nbsp; Fake: {result.fake_percent}%</p>
          {result.frames_analyzed !== undefined && (
            <p style={{ fontSize: "0.85rem", color: "#666" }}>Frames analyzed: {result.frames_analyzed}</p>
          )}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: "40px", maxWidth: "500px", margin: "0 auto", textAlign: "center" },
  preview: { maxWidth: "300px", marginTop: "20px", borderRadius: "8px" },
  button: { marginTop: "20px", padding: "10px 24px", fontSize: "1rem", backgroundColor: "#2563eb", color: "white", border: "none", borderRadius: "6px", cursor: "pointer" },
  error: { color: "red", marginTop: "10px" },
  resultBox: { marginTop: "30px", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" },
};

export default DashboardPage;