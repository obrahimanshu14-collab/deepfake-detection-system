import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App.jsx";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";
const app = (
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);

createRoot(document.getElementById("root")).render(
  googleClientId ? <GoogleOAuthProvider clientId={googleClientId}>{app}</GoogleOAuthProvider> : app
);
