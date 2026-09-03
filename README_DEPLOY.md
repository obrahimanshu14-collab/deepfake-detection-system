# Veritas — Deployment Checklist

## Backend (Render Web Service)

Root directory: `backend`

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Use a backend instance with at least 2 GB RAM for the current MediaPipe + PyTorch workload.

Required environment variables:

```text
DATABASE_URL=<PostgreSQL connection string>
SECRET_KEY=<strong random secret>
CORS_ORIGINS=<frontend URL>
GOOGLE_CLIENT_ID=<Google OAuth web client ID>
ADMIN_EMAILS=<admin email>
RAZORPAY_KEY_ID=<Razorpay key, optional>
RAZORPAY_KEY_SECRET=<Razorpay secret, optional>
```

`GOOGLE_CLIENT_ID` can be left empty when Google sign-in is not needed. Razorpay keys can be left empty to disable payments cleanly.

The model files are shipped in `backend/models/` and are loaded using paths independent of the server working directory.

## Frontend (Render Static Site)

Root directory: `frontend`

Build command:

```bash
npm ci && npm run build
```

Publish directory:

```text
dist
```

Environment variables are injected at build time:

```text
VITE_API_BASE_URL=<deployed backend URL>
VITE_GOOGLE_CLIENT_ID=<same Google web client ID>
```

The Render Blueprint already includes an SPA rewrite so routes such as `/dashboard` work on refresh.

## Local run

Backend:

```powershell
cd backend
..\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Do not commit `.env` files or API/payment credentials.
