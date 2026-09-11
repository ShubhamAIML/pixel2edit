# PIXEL2EDIT - Render Deployment Guide

Follow these steps to deploy **PIXEL2EDIT** on [Render](https://render.com) for free:

---

## 1. Push Your Code to GitHub
Make sure your repository has the following files ready (already created for you):
- `requirements.txt` (includes `gunicorn`, `Flask`, `opencv-python-headless`, etc.)
- `Procfile` (`web: gunicorn "app:app" --bind 0.0.0.0:$PORT --workers 2 --timeout 120`)
- `render.yaml` (Blueprint specification)
- `runtime.txt` (`python-3.12.5`)

---

## 2. Create a Web Service on Render

### Option A: Automatic via Blueprint (Easiest)
1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository (`PIXEL2EDIT`).
4. Render will automatically detect `render.yaml`.
5. Under Environment Variables, set your `GEMINI_API_KEY`.
6. Click **Apply**.

---

### Option B: Manual Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `pixel2edit`
   - **Language**: `Python 3`
   - **Region**: Closest to you (e.g., Singapore, Oregon, Frankfurt)
   - **Branch**: `main` (or `master`)
   - **Build Command**: `pip install -r requirements.txt && pip install gunicorn`
   - **Start Command**: `python -m gunicorn "app:app" --bind 0.0.0.0:$PORT --workers 2 --timeout 120 || python app.py`
   - **Plan**: `Free`

---

## 3. Add Environment Variables on Render
In the **Environment** tab of your Render Web Service, add:

| Key | Value | Notes |
|---|---|---|
| `GEMINI_API_KEY` | `your_actual_gemini_api_key` | **Required** from Google AI Studio |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Default active model |
| `FLASK_DEBUG` | `False` | Production mode |
| `SECRET_KEY` | *(generate a random string)* | Session & security key |
| `PYTHON_VERSION` | `3.12.5` | Recommended Python version |

---

## 4. Deploy & Verify
1. Click **Deploy Web Service**.
2. Once the build finishes, your site will be live at:
   `https://<your-service-name>.onrender.com`
3. Test by uploading a design or flyer — Gemini Flash will reconstruct the layout into interactive, editable elements.
