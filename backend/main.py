"""hermes-gw backend — FastAPI orchestrator for Hermes Agent gateways.

Routes:
  POST /api/chat       — Send a message, returns SSE stream from Hermes gateway.
  GET  /api/sessions   — List chat sessions from the user's gateway.
  GET  /api/sessions/{session_id}/messages — Message history for a session.
  GET  /health         — Orchestrator health check.
"""

from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncGenerator, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from auth import create_token, get_current_user
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

# CORS — allow frontend (any origin for now, CloudFront or ALB direct)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Proxy helpers
# ---------------------------------------------------------------------------

async def _get_gateway_info(user: dict) -> dict:
    """Resolve the user's gateway port and API key, return base URL and auth header."""
    user_id = user["user_id"]
    profile = user["profile"]
    try:
        gw = gateway_manager.get_gateway(user_id)
        if gw is None or not await gateway_manager._is_healthy(gw):
            port = await gateway_manager.get_or_spawn(user_id, profile)
            gw = gateway_manager.get_gateway(user_id)
        else:
            gw.touch()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {
        "base_url": f"http://127.0.0.1:{gw.port}",
        "api_key": gw.api_key if gw else "",
    }


async def _proxy_get(user: dict, path: str, params: Optional[dict] = None) -> dict:
    """Proxy a GET request to the user's Hermes gateway."""
    info = await _get_gateway_info(user)
    url = f"{info['base_url']}{path}"
    headers = {"Authorization": f"Bearer {info['api_key']}"} if info["api_key"] else {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


async def _proxy_stream(user: dict, path: str, body: dict, session_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
    """Proxy a streaming POST request to the user's Hermes gateway.

    Reads the SSE stream from the gateway and yields raw bytes to the client.
    If session_id is provided, passes it as X-Hermes-Session-Id header for context continuity.
    Injects keepalive comments every 15s to prevent CloudFront/ALB timeouts.
    """
    import asyncio as _asyncio
    info = await _get_gateway_info(user)
    url = f"{info['base_url']}{path}"
    headers = {"Authorization": f"Bearer {info['api_key']}"} if info["api_key"] else {}
    if session_id:
        headers["X-Hermes-Session-Id"] = session_id
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=body, headers=headers) as resp:
            if resp.status_code >= 400:
                error_body = await resp.aread()
                raise HTTPException(status_code=resp.status_code, detail=error_body.decode(errors="replace"))
            # Extract session_id from gateway response headers
            gw_session_id = resp.headers.get("X-Hermes-Session-Id", "")
            if gw_session_id:
                yield f"data: {{\"session_id\": \"{gw_session_id}\"}}\n\n".encode()
            # Stream chunks with keepalive injection
            KEEPALIVE = b": keepalive\n\n"
            stream = resp.aiter_bytes()
            while True:
                chunk_task = _asyncio.ensure_future(stream.__anext__())
                done, _ = await _asyncio.wait([chunk_task], timeout=15.0)
                if done:
                    try:
                        chunk = chunk_task.result()
                        yield chunk
                    except StopAsyncIteration:
                        break
                else:
                    chunk_task.cancel()
                    yield KEEPALIVE


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check for the orchestrator itself."""
    return {"status": "ok", "gateways": len(gateway_manager._gateways)}


@app.post("/api/auth/login")
async def login(request: Request):
    """Login — returns a JWT for the given username."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    username = body.get("username", "").strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    try:
        token = create_token(username)
    except ValueError:
        raise HTTPException(status_code=401, detail="Unknown user")

    return {"token": token, "user": username}


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

    # Extract session_id from the original request for context continuity
    frontend_session_id = body.pop("session_id", None) if "message" in body and "messages" not in body else body.get("session_id")
    if frontend_session_id and "message" in body and "messages" not in body:
        pass  # already popped
    # Simple format: {"message": "hello"}  -> convert to chat completions
    if "message" in body and "messages" not in body:
        body = {
            "model": body.get("model", "hermes"),
            "messages": [{"role": "user", "content": body["message"]}],
            "stream": True,
            "reasoning_effort": body.get("reasoning_effort", "medium"),
        }
    else:
        body.setdefault("stream", True)
        body.setdefault("model", "hermes")
        body.setdefault("reasoning_effort", "medium")

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in _proxy_stream(user, "/v1/chat/completions", body, frontend_session_id):
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
    data = await _proxy_get(user, "/api/sessions", params={"limit": limit, "offset": offset})
    # Hermes gateway returns {"object":"list", "data":[...], ...} — extract array
    return data.get("data", data) if isinstance(data, dict) else data


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Get message history for a specific session."""
    data = await _proxy_get(user, f"/api/sessions/{session_id}/messages")
    # Hermes gateway returns {"object":"list", "session_id":"...", "data":[...]} — extract array
    return data.get("data", data) if isinstance(data, dict) else data


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
