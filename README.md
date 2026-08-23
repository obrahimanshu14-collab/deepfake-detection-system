# Deepfake Detection System — Project README

**Status:** Core features complete (image/video/audio detection, live webcam, admin console, payment gateway, lip-sync). UI redesigned with a custom "verification lab" visual identity. Deployment in progress.

---

## 1. What This Project Is

A full-stack deepfake detection platform supporting **image, video, audio, and live webcam** analysis, plus a Google Sign-In auth flow and a simulated trial/payment system. Users get a 5-tier verdict (REAL / Possibly Real / Uncertain / Possibly Fake / FAKE) with an explicit REAL% / FAKE% breakdown.

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), Tailwind CSS |
| Backend | FastAPI, WebSocket support |
| Database | PostgreSQL + SQLAlchemy |
| Image/Video ML | PyTorch + torchvision (MobileNetV2) |
| Audio ML | Same architecture, applied to mel-spectrograms |
| Auth | JWT + bcrypt, Google OAuth |
| Payments | Razorpay (test mode) |

---

## 3. Completed Features

- **Authentication**: Email/password signup+login, Google Sign-In, JWT-based sessions, admin role
- **Image Detection**: MobileNetV2 CNN, 89.17% validation accuracy, 80% external-test accuracy
- **Video Detection**: CNN frame-sampling + rPPG + lip-sync ensemble (see Known Limitations)
- **Audio Detection**: Spectrogram-based CNN, 98.41% validation accuracy
- **Live Webcam Detection**: WebSocket streaming, session-based final verdict
- **Admin Console**: User list, prediction stats, label/type breakdowns
- **Trial + Payment**: 5 free checks per user, Razorpay test-mode upgrade flow
- **History Page**: Per-user past prediction log

---

## 4. Known Limitations (Documented Honestly)

1. **AI-generated talking-avatar videos (e.g. HeyGen-style) are not reliably detected.** The image/video CNN was trained on fully GAN-generated static faces (StyleGAN), so it learned texture artifacts specific to that generation method. Confirmed by testing: HeyGen-style samples were classified REAL/Possibly Real by the ensemble.

2. **rPPG signal is not yet reliably discriminative.** Calibration on a small sample (10 videos) showed negligible or inconsistent real/fake separation, likely due to compression (WhatsApp-exported test videos). Weighted low (0.05) in the ensemble pending a larger, less-compressed calibration set.

3. **Lip-sync signal (correlation between MediaPipe lip-landmark movement and audio energy) is implemented but also not yet calibrated.** Adding it at a moderate weight measurably hurt overall accuracy on the same 10-video test set (66.67% → 55.56%), so it is currently weighted low (0.05), same as rPPG, pending recalibration with more samples.

4. **Current ensemble weights**: `{cnn: 0.90, rppg: 0.05, lipsync: 0.05}` — the CNN remains the dominant, trusted signal; rPPG and lip-sync are logged for future recalibration but do not meaningfully influence verdicts yet.

---

## 5. Roadmap

| Feature | Status |
|---|---|
| Image/Video/Audio detection | Complete |
| Live webcam detection | Complete |
| Admin console | Complete |
| Trial limits + payment (test mode) | Complete |
| Google Sign-In | Complete |
| Lip-sync detection | Implemented, uncalibrated |
| rPPG calibration | Pending more data |
| ESRGAN | Not started |
| Deployment | In progress (Render + Vercel) |

---

## 6. Setup Instructions

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### Frontend
```powershell
cd frontend
npm run dev
```

### Database
PostgreSQL must be running locally; connection string in `backend/.env` (`DATABASE_URL`).

### Model training
```powershell
cd backend
python training\download_dataset.py
python training\data_manifest.py
python training\train.py

python training\download_audio_dataset.py
python training\audio_manifest.py
python training\train_audio.py
```

### External validation
```powershell
python training\evaluate_external.py
python training\evaluate_external_video.py
python training\calibrate_rppg.py
```