# Veritas — Deepfake Detection Platform

**Status:** Deployment-ready application build for the current ML pipeline.

Veritas is a full-stack platform for analyzing **images, videos, audio, and live webcam sessions** for signals associated with manipulated or synthetic media. Results use five confidence bands: **REAL, Possibly Real, Uncertain, Possibly Fake, FAKE**.

## Stack

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** FastAPI + WebSocket
- **Database:** PostgreSQL + SQLAlchemy
- **Image/Video model:** PyTorch MobileNetV2
- **Audio model:** MobileNetV2 on mel-spectrogram images
- **Face processing:** MediaPipe with OpenCV Haar fallback
- **Additional video signals:** rPPG + lip-sync correlation
- **Auth:** JWT + bcrypt + Google Sign-In
- **Payments:** Razorpay integration (optional; test/live keys are configured outside the repository)

## Product features

- Email/password signup and login
- Google Sign-In when configured
- Protected dashboard, history, live detection, upgrade, and admin pages
- Five free detection checks by default
- Razorpay weekly/monthly/annual plans
- Per-user prediction history with private file access
- Image, video and audio upload size/type validation
- Live webcam WebSocket inference
- Admin metrics and user overview
- Health/readiness endpoints for deployment monitoring
- Environment-based CORS, API URLs, JWT settings, model paths, upload storage and payment configuration
- Render Blueprint for separate backend and frontend services

## Model notes

The application deliberately does **not** claim 100% certainty. The current trained image/video detector is MobileNetV2-based, while rPPG and lip-sync are supporting signals rather than independently validated deep-learning detectors. The current ensemble remains conservative:

```text
CNN      90%
rPPG      5%
lip-sync  5%
```

Existing validation results from the project are retained as historical experiment results; they should not be presented as a universal real-world accuracy guarantee.

## Local setup

Create `backend/.env` from `backend/.env.example` and `frontend/.env` from `frontend/.env.example`.

### Backend

```powershell
cd backend
..\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Training

```powershell
cd backend
python training\download_dataset.py
python training\data_menifest.py
python training\train.py

python training\download_audio_dataset.py
python training\audio_manifest.py
python training\train_audio.py
```

The trained inference checkpoints are shipped under `backend/models/`.

## Deployment

See **[README_DEPLOY.md](README_DEPLOY.md)** for the final deployment checklist and environment variables.

For Render, the included `render.yaml` defines a Python backend and a Vite static frontend. The backend uses the standard Uvicorn start command and the frontend includes an SPA rewrite for React Router.

### Production storage note

Prediction files are stored under the configured `UPLOADS_DIR`. For a true production SaaS rollout, use durable private object storage (or a paid persistent disk) rather than relying on an ephemeral web-service filesystem.

### Security rules

Never commit:

- `.env` files
- Google/Razorpay secrets
- database passwords
- `kaggle.json`
- private API keys

The repository ignores local environment files and generated upload/data directories.
