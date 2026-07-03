"""hermes-gw backend — FastAPI orchestrator for Hermes Agent gateways.

Routes:
  POST /api/chat       — Send a message, returns SSE stream from Hermes gateway.
  GET  /api/sessions   — List chat sessions from the user's gateway.
  GET  /api/sessions/{session_id}/messages — Message history for a session.
  GET  /health         — Orchestrator health check.
"""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from auth import get_current_user
from gateway_manager import gateway_manager

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle for the FastAPI app."""
    await gateway_manager.start()
    logger.info("hermes-gw backend started")
    yield
    await gateway_manager.stop()
    logger.info("hermes-gw backend stopped")


app = FastAPI(title="hermes-gw", version="0.1.0", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Proxy helpers
# ---------------------------------------------------------------------------

async def _get_gateway_url(user: dict) -> str:
    """Resolve the user's gateway port and return its base URL."""
    user_id = user["user_id"]
    profile = user["profile"]
    try:
        port = await gateway_manager.get_or_spawn(user_id, profile)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return f"http://127.0.0.1:{port}"


async def _proxy_get(user: dict, path: str, params: Optional[dict] = None) -> dict:
    """Proxy a GET request to the user's Hermes gateway."""
    base_url = await _get_gateway_url(user)
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


async def _proxy_stream(user: dict, path: str, body: dict) -> AsyncGenerator[bytes, None]:
    """Proxy a streaming POST request to the user's Hermes gateway.

    Reads the SSE stream from the gateway and yields raw bytes to the client.
    """
    base_url = await _get_gateway_url(user)
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=body) as resp:
            if resp.status_code >= 400:
                error_body = await resp.aread()
                raise HTTPException(status_code=resp.status_code, detail=error_body.decode(errors="replace"))
            async for chunk in resp.aiter_bytes():
                yield chunk


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check for the orchestrator itself."""
    return {"status": "ok", "gateways": len(gateway_manager._gateways)}


@app.post("/api/chat")
async def chat(request: Request, user: dict = Depends(get_current_user)):
    """Send a chat message and stream the response via SSE.

    The request body is forwarded to the Hermes gateway's /v1/chat/completions
    endpoint. The response is streamed as SSE (text/event-stream).
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Support both OpenAI-compatible and simple message formats
    # Simple format: {"message": "hello"}  -> convert to chat completions
    if "message" in body and "messages" not in body:
        body = {
            "model": body.get("model", "hermes"),
            "messages": [{"role": "user", "content": body["message"]}],
            "stream": True,
        }
    else:
        body.setdefault("stream", True)
        body.setdefault("model", "hermes")

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in _proxy_stream(user, "/v1/chat/completions", body):
                yield chunk.decode(errors="replace")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stream error for user={user['user_id']}: {e}")
            yield f"data: [ERROR] {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/sessions")
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
):
    """List chat sessions from the user's Hermes gateway."""
    return await _proxy_get(user, "/api/sessions", params={"limit": limit, "offset": offset})


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Get message history for a specific session."""
    return await _proxy_get(user, f"/api/sessions/{session_id}/messages")


# ---------------------------------------------------------------------------
# CLI helper: generate a token for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from auth import create_token

    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        try:
            token = create_token(user_id)
            print(token)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
