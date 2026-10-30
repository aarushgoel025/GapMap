# GapMap Cloud Deployment Guide

This guide covers deploying **GapMap** to production:
- **Frontend (React 19 + Vite)**: Deployed on **Vercel**
- **Backend (FastAPI + Python)**: Deployed on **Render** (or **Railway** / **Koyeb**)

---

## 🏗️ Architecture Overview

```
                      ┌──────────────────────────────────────────┐
                      │             User's Browser               │
                      └────────────────────┬─────────────────────┘
                                           │
                    HTTPS Requests         │
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │             Vercel (Frontend)            │
                      │        https://gapmap.vercel.app         │
                      └────────────────────┬─────────────────────┘
                                           │
                            API Calls via  │  VITE_API_BASE_URL
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │          Render / Railway (Backend)      │
                      │      https://gapmap-api.onrender.com     │
                      │                                          │
                      │   - FastAPI + Uvicorn                    │
                      │   - Gemini 2.5 + Mistral Consensus       │
                      │   - 3-Layer ATS Scoring Engine           │
                      │   - Supabase / JSON Store                │
                      └──────────────────────────────────────────┘
```

---

## 🚀 Step 1: Push Changes to GitHub

Ensure all your latest files (including the newly added `vercel.json`, `Procfile`, and `render.yaml`) are committed to GitHub:

```bash
git add .
git commit -m "feat: prepare repository for Vercel and Render cloud deployment"
git push origin main
```

---

## 🐍 Step 2: Deploy Backend to Render (Free Tier)

Render provides a native Python web service that runs FastAPI with zero hassle.

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New +** → **Web Service**.
3. Connect your **GapMap** repository.
4. Configure the settings:
   - **Name**: `gapmap-api` (or any name you choose)
   - **Region**: Closest to you (e.g., Singapore, Frankfurt, or Oregon)
   - **Branch**: `main`
   - **Root Directory**: Leave blank (uses repository root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Click **Advanced** → **Add Environment Variable**:
   | Key | Value | Notes |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Recommended Python version |
   | `GEMINI_API_KEY` | `AIzaSy...` | Your Google AI Studio API key |
   | `GEMINI_MODEL` | `gemini-2.5-flash` | Default Gemini model |
   | `MISTRAL_API_KEY`| `...` | Your Mistral API key |
   | `MISTRAL_MODEL` | `mistral-small-latest` | Default Mistral model |
   | `CORS_ORIGINS` | `*` | Allows calls from your Vercel URL |
   | `GITHUB_TOKEN` | *(Optional)* | For higher GitHub verification rate limits |
   | `SUPABASE_URL` | *(Optional)* | If using cloud Supabase storage |
   | `SUPABASE_KEY` | *(Optional)* | If using cloud Supabase storage |

6. Click **Create Web Service**.
7. Wait 2-3 minutes until Render finishes building. Copy your public backend URL:
   `https://gapmap-api-xxxx.onrender.com`

> **Verification**: Visit `https://gapmap-api-xxxx.onrender.com/health` in your browser. It should return `{"status": "ok"}`.

---

## ⚡ Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **Add New...** → **Project**.
3. Import your **GapMap** GitHub repository.
4. In the configuration screen:
   - **Project Name**: `gapmap` (or your choice)
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and select `frontend` *(or leave `./` since root `vercel.json` is configured)*.
   - **Build and Output Settings**:
     - Build Command: `npm run build`
     - Output Directory: `dist`
5. Expand **Environment Variables** and add:
   | Key | Value |
   | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://gapmap-api-xxxx.onrender.com` *(paste your backend URL from Step 2, without trailing slash)* |

6. Click **Deploy**.
7. In ~30-45 seconds, Vercel will build and deploy your app, giving you a live URL like:
   `https://gapmap.vercel.app`

---

## ✅ Step 4: Verification Checklist

Once both services are deployed:
1. Open your Vercel URL: `https://gapmap.vercel.app`
2. Scroll to the footer: Verify that it says `Connected to FastAPI Backend at https://gapmap-api-xxxx.onrender.com`.
3. Click **"Launch Pipeline"**:
   - Run **Step 1 (JD Analytics)**: Check that the sample JDs load instantly from cache.
   - Run **Step 2 (Resume Parsing)**: Verify that stuffing detection and GitHub check work.
   - Run **Step 4 (Talent Check)**: Test the What-If slider.
   - Run **Step 5 (Skill Matching)**: Verify that the 4×6 Heatmap Matrix opens smoothly.

---

## 💡 Alternative Options

### Option B: Deploying Backend on Railway.app
If you prefer Railway over Render:
1. Go to [railway.app](https://railway.app), click **New Project** → **Deploy from GitHub repo**.
2. Railway will automatically detect the `Procfile` and deploy your FastAPI backend.
3. In Railway settings, add the same environment variables (`GEMINI_API_KEY`, etc.).
4. Generate a public domain under **Settings** → **Networking** → **Generate Domain**, and use that URL as `VITE_API_BASE_URL` in Vercel.

