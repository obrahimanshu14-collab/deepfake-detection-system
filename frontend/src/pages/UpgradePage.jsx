import { useState } from "react";
import api from "../services/api";

const PLAN_OPTIONS = [
  { key: "weekly", label: "Weekly", price: "₹29", period: "/week" },
  { key: "monthly", label: "Monthly", price: "₹99", period: "/month", popular: true },
  { key: "annual", label: "Annual", price: "₹899", period: "/year" },
];

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
  const [selectedPlan, setSelectedPlan] = useState("monthly");
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

      const { data: order } = await api.post("/payment/create-order", { plan: selectedPlan });

      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "Veritas",
                prefill: {
          email: localStorage.getItem("user_email") || "",
        },
        description: `${order.plan_label} Plan`,
        handler: async function (response) {
          try {
            await api.post("/payment/verify", {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              plan: selectedPlan,
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
        <h1 className="font-display text-2xl font-semibold text-verdict-real">Upgrade Successful!</h1>
        <p className="mt-2 text-ink/60">You now have unlimited access.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-16 px-6 text-center">
      <div className="text-5xl mb-4">🔒</div>
      <h1 className="font-display text-3xl font-semibold mb-2">Your Free Trial Has Ended</h1>
      <p className="text-ink/60 mb-10">
        You've used all your free checks. Choose a plan to continue with unlimited detection.
      </p>

      <div className="grid md:grid-cols-3 gap-5 mb-8">
        {PLAN_OPTIONS.map((plan) => (
          <button
            key={plan.key}
            onClick={() => setSelectedPlan(plan.key)}
            className={`relative p-6 rounded-sm border text-left transition-colors ${
              selectedPlan === plan.key
                ? "border-signal bg-signal/5"
                : "border-ink/15 hover:border-ink/30"
            }`}
          >
            {plan.popular && (
              <span className="absolute -top-3 left-4 bg-signal text-white text-[10px] font-mono-label uppercase px-2 py-0.5 rounded-sm">
                Popular
              </span>
            )}
            <p className="font-mono-label text-xs uppercase text-ink/40 mb-2">{plan.label}</p>
            <p className="font-display text-2xl font-semibold">
              {plan.price} <span className="text-sm font-normal text-ink/40">{plan.period}</span>
            </p>
          </button>
        ))}
      </div>

      <button
        onClick={handleUpgrade}
        disabled={loading}
        className="bg-signal text-white px-8 py-3 rounded-sm font-medium hover:bg-signal-dark transition-colors disabled:opacity-50 w-full md:w-auto"
      >
        {loading ? "Loading..." : `Upgrade — ${PLAN_OPTIONS.find((p) => p.key === selectedPlan)?.price}${PLAN_OPTIONS.find((p) => p.key === selectedPlan)?.period}`}
      </button>
      {error && <p className="text-verdict-fake mt-4 text-sm">{error}</p>}
    </div>
  );
}

export default UpgradePage;