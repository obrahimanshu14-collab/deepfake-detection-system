import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { GoogleOAuthProvider } from "@react-oauth/google";
import App from "./App.jsx";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

const GOOGLE_CLIENT_ID = "876626181579-ged8ofq1ilk2fqhctns90j74bo2eak4s.apps.googleusercontent.com";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ErrorBoundary>
      <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
        <App />
      </GoogleOAuthProvider>
    </ErrorBoundary>
  </StrictMode>
);