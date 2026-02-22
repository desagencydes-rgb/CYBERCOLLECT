"""
AI Chat API – Ollama LLM with auto-detection and streaming SSE
Auto-pings Ollama on each request. If available (locally or on server), streams response.
If unavailable, returns a clear status message.
"""
import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter()

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """You are CyberCollect AI, an expert assistant embedded inside a waste collection route optimization system.
You help users understand:
- Graph theory and Dijkstra's algorithm (Level 1)
- Bin packing and greedy truck-zone assignments (Level 2)
- Weekly scheduling with time windows and driver constraints (Level 3)
- Vehicle Routing Problem (VRP) solved with nearest-neighbor + Tabu search (Level 4)
- Real-time IoT simulation and dynamic re-optimization (Level 5)

You respond in a concise, technical but approachable way. Use markdown formatting.
When relevant, refer to the current optimization context provided by the user.
"""


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None  # Current level state injected by frontend
    model: Optional[str] = None


async def _check_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def _stream_ollama(message: str, context: Optional[str], model: str):
    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nCurrent optimization context:\n{context}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        if chunk.get("done"):
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break
                    except json.JSONDecodeError:
                        continue


@router.post("/status")
async def chat_status():
    """Check if Ollama is available on this machine/server."""
    available = await _check_ollama_available()
    if available:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                models = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            models = []
        return {"available": True, "models": models, "endpoint": OLLAMA_BASE_URL}
    return {
        "available": False,
        "message": "Ollama not detected. Install Ollama and run `ollama pull llama3.2:3b` to enable AI chat.",
        "install_url": "https://ollama.com",
    }


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """Stream LLM response via SSE. Auto-detects Ollama availability."""
    model = req.model or DEFAULT_MODEL
    available = await _check_ollama_available()

    if not available:
        async def unavailable_msg():
            msg = ("Ollama is not running on this machine. "
                   "Install it at https://ollama.com and run `ollama pull llama3.2:3b` "
                   "to enable the AI assistant.")
            yield f"data: {json.dumps({'token': msg})}\n\n"
            yield f"data: {json.dumps({'done': True, 'unavailable': True})}\n\n"

        return StreamingResponse(unavailable_msg(), media_type="text/event-stream")

    return StreamingResponse(
        _stream_ollama(req.message, req.context, model),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
