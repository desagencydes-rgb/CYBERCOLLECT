# 🛰️ CyberCollect – Free Deployment Guide ($0 total)

## Option A – Hugging Face Spaces (Recommended, No Credit Card Required)

Hugging Face provides free Docker hosting (16GB RAM, 2 CPUs) with a simple GitHub connection.

1. Create a free account at [huggingface.co](https://huggingface.co/).
2. Go to your Profile and click **New Space**.
3. Name your space (e.g., `CyberCollect`).
4. Under "Select the Space SDK", click **Docker** → **Blank**.
5. Choose "Public" and click **Create Space**.
6. Follow the instructions to link your GitHub repository to the Space (you can directly sync it by pushing to their remote URL or uploading the files).
7. Hugging Face will automatically read the `Dockerfile`, build the image, and serve it. 

Your app will be live at: `https://huggingface.co/spaces/your-username/CyberCollect`

---

## Option B – Render.com (Requires Credit Card for some verifications)

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
