# 🛰️ CyberCollect – Free Deployment Guide ($0 total)

## Option A – Render.com (Recommended, 100% Free)

**Prerequisites:** GitHub account, this repo pushed to GitHub.

### Steps

1. **Fork/push** this repo to your GitHub account.
2. Go to [render.com](https://render.com) → Sign up (free, no credit card).
3. Click **"New +"** → **"Web Service"**.
4. Connect your GitHub repo.
5. Render auto-detects `render.yaml` and configures everything.
6. Click **"Create Web Service"** → Done! 🎉

Your app will be live at: `https://cybercollect.onrender.com` (or similar).

> **Note on AI Chat:** Render's free tier does not have enough compute to run Ollama.
> The AI chat will auto-detect this and tell you. If you upgrade to a paid instance,
> or run the app locally, the full AI chat activates automatically — no config needed.

---

## Option B – Run Locally (Full Features including AI Chat)

### Step 1 – Install dependencies
```bash
cd /path/to/tournees
pip install fastapi uvicorn httpx python-multipart
```

### Step 2 – Start the server
```bash
cd projet_collecte_dechets
uvicorn webapp.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3 – Open the app
Open your browser at: **http://localhost:8000**

### Step 4 (Optional) – Enable AI Chat
Install Ollama from https://ollama.com, then:
```bash
ollama pull llama3.2:3b
ollama serve
```
Refresh the app — AI chat activates automatically! ✅

---

## Option C – Docker Compose (Full local stack with Ollama)

```bash
cd /path/to/tournees
docker-compose up --build
```

Then open: **http://localhost:8000**

To pull the LLM model into the Ollama container:
```bash
docker exec -it tournees-ollama-1 ollama pull llama3.2:3b
```

---

## 💡 Cost Summary

| Component | Cost |
|-----------|------|
| Render.com free tier | $0/mo |
| Ollama LLM (local/self-hosted) | $0 |
| Three.js CDN | $0 |
| Google Fonts CDN | $0 |
| **Total** | **$0** |
