function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto mt-16 px-6">
      <p className="font-mono-label text-xs uppercase text-signal mb-2">Legal</p>
      <h1 className="font-display text-3xl font-semibold mb-8">Privacy Briefing</h1>

      <div className="space-y-6 text-ink/70 leading-relaxed">
        <div>
          <p className="font-medium text-ink mb-1">What we store</p>
          <p className="text-sm">Your email, a hashed password (never plaintext), and every file you check — including a copy of the image, video, or audio itself — so you can revisit your past results from your History page at any time.</p>
        </div>
        <div>
          <p className="font-medium text-ink mb-1">Live Detection</p>
          <p className="text-sm">When you use Live Detection, individual webcam frames are analyzed for the running session. The completed recording can be saved to your account along with its overall verdict.</p>
        </div>
        <div>
          <p className="font-medium text-ink mb-1">Who can see your data</p>
          <p className="text-sm">Only you can see your own prediction history and files. Admin accounts can see aggregate statistics and account metadata, never the content of your uploads.</p>
        </div>
        <div>
          <p className="font-medium text-ink mb-1">Third parties</p>
          <p className="text-sm">Payment processing is handled by Razorpay; we never see or store your card details.</p>
        </div>
      </div>
    </div>
  );
}

export default PrivacyPage;