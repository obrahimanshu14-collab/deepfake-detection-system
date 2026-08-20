import { useNavigate } from "react-router-dom";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Deepfake Detection System</h1>
      <p style={styles.subtitle}>
        Upload an image or video to check whether it is REAL or a DEEPFAKE, powered by AI.
      </p>
      <div style={styles.buttonGroup}>
        <button style={styles.primaryButton} onClick={() => navigate("/signup")}>
          Get Started
        </button>
        <button style={styles.secondaryButton} onClick={() => navigate("/login")}>
          Login
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    textAlign: "center",
    padding: "0 20px",
  },
  title: {
    fontSize: "2.5rem",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "1.1rem",
    color: "#555",
    maxWidth: "500px",
    marginBottom: "30px",
  },
  buttonGroup: {
    display: "flex",
    gap: "15px",
  },
  primaryButton: {
    padding: "12px 24px",
    fontSize: "1rem",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  secondaryButton: {
    padding: "12px 24px",
    fontSize: "1rem",
    backgroundColor: "white",
    color: "#2563eb",
    border: "2px solid #2563eb",
    borderRadius: "8px",
    cursor: "pointer",
  },
};

export default LandingPage;