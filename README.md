# Deepfake Detection System — Project README

Status: Active development. Core features (image/video/audio detection, live webcam detection, admin console) implemented. Payment gateway and UI polish pending, targeted before the next mentor review.

---

## 1. What This Project Is

A full-stack deepfake detection platform supporting image, video, audio, and live webcam analysis. Users sign up, submit content, and receive a 5-tier verdict (REAL / Possibly Real / Uncertain / Possibly Fake / FAKE) with an explicit REAL% / FAKE% breakdown, rather than a blunt binary answer — since no detector can be 100% certain and the UI should reflect that honestly.

The system is built as several independent, swappable modules (frontend, backend, ML models, database) so new detection signals can be added over time without rewriting existing code.

---

## 2. Tech Stack

| Layer          | Technology |
|---             |---|
| Frontend       | React (Vite) |
| Backend        | FastAPI (Python), WebSocket support for live detection |
| Database       | PostgreSQL + SQLAlchemy ORM |
| Image/Video ML | PyTorch + torchvision (MobileNetV2 backbone) |
| Audio ML       | Same MobileNetV2 architecture, applied to mel-spectrogram images (librosa) |
| Face detection | MediaPipe, with automatic OpenCV Haar Cascade fallback |
| Auth           | JWT (python-jose) + bcrypt password hashing (passlib) |

---

## 3. Architecture

```
React Frontend (localhost:5173)
        |
        v  REST API + WebSocket, JWT-authenticated
FastAPI Backend (localhost:8000)
    |            |             |
    v            v             v
Image/Video   Audio Model   PostgreSQL
CNN + rPPG    (spectrogram)  Database
```

Frontend and backend communicate only through a defined API contract (REST for image/video/audio uploads, WebSocket for the continuous live-webcam stream). This lets any client type (web, future mobile app, browser extension) reuse the same backend without modification.

---

## 4. Database Schema

| Table                                     | Purpose |
|---                                        |---|
| `users`                                   | Registered users (email, hashed password, admin flag) |
| `predictions`                             | Every check performed (image/video/audio), linked to a user |
| `admin_logs`                              | Admin action audit trail |
| `organizations`, `api_keys`, `usage_logs` | Reserved for future paid-API access (schema exists; not yet wired to a payment flow) |

---

## 5. Completed Features

### Authentication & Core Backend
- JWT-based signup/login, bcrypt password hashing
- Role-based access control (`is_admin` flag), enforced via a dedicated FastAPI dependency
- CORS configured for the frontend origin

### Image Detection
- MobileNetV2 (ImageNet-pretrained, partially frozen) + custom classification head
- Trained on an 8% subset (~11,200 images) of Kaggle's "140k Real and Fake Faces" (FFHQ real + StyleGAN fake)
- Validation accuracy: 89.17%; external (held-out, hand-picked) test accuracy: 80%

### Video Detection
- Frame-sampling (every 15th frame, up to 30 frames) reusing the image CNN
- rPPG (remote photoplethysmography) signal analysis added as a second signal, using the POS algorithm (RGB-channel projection, more robust to compression than naive green-channel analysis)
- CNN and rPPG combined into a single weighted verdict (currently CNN 0.95 / rPPG 0.05 — see Known Limitations)

### Audio Detection
- Audio converted to mel-spectrograms (librosa), classified with the same MobileNetV2-based architecture pattern as the image model (transfer learning, not a from-scratch audio model)
- Trained on ~16,800 labeled real/AI-generated speech clips (Kaggle: "Deepfake Audio Dataset — Fake vs Real Speech")
- Validation accuracy: 98.41%

### Live Webcam Detection
- WebSocket endpoint (`/live/webcam`) streams one frame per second from the browser, returns a live REAL/FAKE verdict per frame
- Reuses the same trained image model and face-detection pipeline as the upload-based flow — no separate model needed

### Admin Console
- `/admin/stats`: total users, total predictions, REAL/FAKE breakdown, per-file-type breakdown
- `/admin/users`: full user list with per-user prediction counts
- Protected by an admin-only backend dependency; frontend only shows the "Admin" nav link to admin accounts (decoded from the JWT)

### Frontend
- Pages: Landing, Signup, Login, Dashboard (image/video/audio upload), Live Detection, History, Admin
- Persistent, auth-aware Navbar
- Axios service layer with automatic JWT attachment

---

## 6. Known Limitations (Documented Honestly)

1. The image/video model does not reliably detect AI-generated talking-avatar videos (e.g., HeyGen-style content, where a real person's likeness is animated/lip-synced rather than the entire face being GAN-generated). The training dataset consists of fully GAN-generated static faces, so the model learned texture artifacts specific to that generation method — talking-avatar tools often start from a real source face, so per-frame texture looks authentic. Confirmed by testing: a HeyGen sample was classified "REAL" (94.6%) by the CNN alone.

2. rPPG signal is not yet reliably discriminative on compressed, real-world video. Calibration on a small sample (5 real / 5 fake, later 10 total) showed negligible separation between real and fake videos (mean peak-ratio: REAL 0.082 vs FAKE 0.087 — statistically indistinguishable at this sample size, and in the wrong direction). This is a known, documented challenge in rPPG research: heavy compression (e.g., WhatsApp export) destroys much of the fine-grained color signal rPPG depends on. The POS algorithm (more robust than naive green-channel analysis) was implemented, but did not resolve this on the available compressed test samples. Mitigation: rPPG is weighted very low in the ensemble (0.05) so it cannot degrade the otherwise-reliable CNN verdict, while still logging data for recalibration as more samples are collected.

3. Both limitations above are the direct motivation for the planned lip-sync detection module (not yet implemented), which targets exactly the temporal/audio-mismatch category of deepfake that a single-frame CNN and a compression-degraded rPPG signal both currently miss.

---

## 7. Roadmap

| Phase | Feature                                                          | Status |
|---    |---                                                               |---|
| A     | Image detection (CNN)                                            | Complete |
| A     | Video detection (CNN + rPPG ensemble)                            | Complete, rPPG weighted low pending better calibration data |
| B     | Audio detection                                                  | Complete |
| C     | Live webcam detection                                            | Complete |
| —     | Admin console                                                    | Complete |
| D     | Lip-sync detection                                               | Not started |
| E     | ESRGAN (quality enhancement or GAN-fingerprint — use case undecided) | Not started |
| —     | Payment gateway + paid API access (trial limit, then pay-per-use) | Not started — next priority |
| —     | UI/visual design polish                                           | Not started — next priority |
| —     | Deployment (currently local-only)                                 | Not started |

---

## 8. Setup Instructions

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```
Runs at `http://127.0.0.1:8000` (interactive docs at `/docs`).

### Frontend
```powershell
cd frontend
npm run dev
```
Runs at `http://localhost:5173`.

### Database
PostgreSQL must be running locally; connection string is in `backend/.env` (`DATABASE_URL`).

### Model training (only needed to retrain)
```powershell
cd backend
python training\download_dataset.py          # image dataset
python training\data_manifest.py
python training\train.py

python training\download_audio_dataset.py     # audio dataset
python training\audio_manifest.py
python training\train_audio.py
```

### External validation
```powershell
python training\evaluate_external.py          # image
python training\evaluate_external_video.py    # video (CNN + rPPG)
python training\calibrate_rppg.py             # rPPG-specific calibration check
```
Place test files in `backend\data\external_test\{real,fake}` (images) or
`backend\data\external_test_video\{real,fake}` (videos).
