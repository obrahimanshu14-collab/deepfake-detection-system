import { useState } from "react";
import api from "../services/api";

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) return resolve(true);
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

function UpgradePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function handleUpgrade() {
    setLoading(true);
    setError("");
    try {
      const scriptLoaded = await loadRazorpayScript();
      if (!scriptLoaded) {
        setError("Could not load payment gateway. Check your internet connection.");
        return;
      }

      const { data: order } = await api.post("/payment/create-order");

      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "Deepfake Detector",
        description: "Unlimited Access Upgrade",
        handler: async function (response) {
          try {
            await api.post("/payment/verify", {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            setSuccess(true);
          } catch {
            setError("Payment verification failed.");
          }
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not start payment. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="max-w-md mx-auto mt-20 text-center">
        <h1 className="text-2xl font-bold text-green-600">Upgrade Successful!</h1>
        <p className="mt-2 text-gray-600">You now have unlimited access.</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto mt-20 text-center p-8 border rounded-xl shadow-sm">
      <div className="text-5xl mb-4">🔒</div>
      <h1 className="text-2xl font-bold mb-2">Your Free Trial Has Ended</h1>
      <p className="text-gray-600 mb-6">
        You've used all your free checks. Upgrade now to continue using unlimited detection.
      </p>
      <button
        onClick={handleUpgrade}
        disabled={loading}
        className="bg-brand-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-brand-700 transition disabled:opacity-50 w-full"
      >
        {loading ? "Loading..." : "Upgrade — ₹99/month"}
      </button>
      {error && <p className="text-red-500 mt-4 text-sm">{error}</p>}
    </div>
  );
}

export default UpgradePage;