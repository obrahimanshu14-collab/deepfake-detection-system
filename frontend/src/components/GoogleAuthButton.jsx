import { useEffect, useRef, useState } from "react";
import { googleAuth } from "../services/authService";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "";

function GoogleAuthButton({ mode = "signin", onSuccess, onError }) {
  const buttonRef = useRef(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return;

    let cancelled = false;
    const scriptId = "google-identity-services";

    const renderButton = () => {
      if (cancelled || !window.google?.accounts?.id || !buttonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: async (response) => {
          try {
            await googleAuth(response.credential);
            onSuccess?.();
          } catch (err) {
            onError?.(err.response?.data?.detail || "Google sign-in failed. Please try again.");
          }
        },
      });

      buttonRef.current.innerHTML = "";
      window.google.accounts.id.renderButton(buttonRef.current, {
        type: "standard",
        theme: "outline",
        size: "large",
        shape: "rectangular",
        text: mode === "signup" ? "signup_with" : "signin_with",
        width: 360,
      });
      setReady(true);
    };

    const existing = document.getElementById(scriptId);
    if (existing) {
      renderButton();
      return () => {
        cancelled = true;
      };
    }

    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = renderButton;
    document.head.appendChild(script);

    return () => {
      cancelled = true;
    };
  }, [mode, onError, onSuccess]);

  if (!GOOGLE_CLIENT_ID) {
    return (
      <div className="google-unconfigured">
        <strong>Google sign-in</strong>
        <span>Add VITE_GOOGLE_CLIENT_ID to frontend/.env to enable it.</span>
      </div>
    );
  }

  return <div className={`google-auth-wrap ${ready ? "is-ready" : ""}`} ref={buttonRef} />;
}

export default GoogleAuthButton;
