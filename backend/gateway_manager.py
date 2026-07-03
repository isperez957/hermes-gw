"""GatewayManager — spawns, tracks, and reaps Hermes gateway processes.

Architecture:
  - One Hermes gateway per user profile, each on its own port starting at 8642.
  - Gateways are spawned lazily on first request.
  - Idle gateways (>30 min without activity) are killed by a background reaper.
  - Health is checked via http://127.0.0.1:{port}/health before returning a port.
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

GATEWAY_BASE_PORT = 8642
IDLE_TIMEOUT_SECONDS = 30 * 60  # 30 minutes
HEALTH_CHECK_TIMEOUT = 5.0  # seconds
STARTUP_GRACE_PERIOD = 15.0  # seconds to wait for gateway to come up


@dataclass
class Gateway:
    port: int
    process: asyncio.subprocess.Process
    last_used: float = field(default_factory=time.monotonic)

    def touch(self) -> None:
        self.last_used = time.monotonic()

    @property
    def idle_seconds(self) -> float:
        return time.monotonic() - self.last_used

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


class GatewayManager:
    """Manages the lifecycle of Hermes gateway processes."""

    def __init__(self) -> None:
        self._gateways: dict[str, Gateway] = {}  # user_id -> Gateway
        self._lock = asyncio.Lock()
        self._next_port = GATEWAY_BASE_PORT
        self._reaper_task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        """Start the background reaper task."""
        if self._reaper_task is None:
            self._reaper_task = asyncio.create_task(self._reaper_loop())
            logger.info("GatewayManager reaper started")

    async def stop(self) -> None:
        """Stop the reaper and kill all gateways."""
        if self._reaper_task:
            self._reaper_task.cancel()
            try:
                await self._reaper_task
            except asyncio.CancelledError:
                pass
            self._reaper_task = None

        # Kill all running gateways
        for user_id, gw in list(self._gateways.items()):
            await self._kill_gateway(user_id, gw)
        self._gateways.clear()
        logger.info("GatewayManager stopped, all gateways killed")

    async def get_or_spawn(self, user_id: str, profile: str) -> int:
        """Return the port for a user's gateway, spawning it if necessary.

        Also touches the gateway to reset its idle timer.
        """
        gw = self._gateways.get(user_id)

        if gw is not None and await self._is_healthy(gw):
            gw.touch()
            return gw.port

        # Gateway missing or unhealthy — (re)spawn
        async with self._lock:
            # Double-check under lock in case another task just spawned it
            gw = self._gateways.get(user_id)
            if gw is not None and await self._is_healthy(gw):
                gw.touch()
                return gw.port

            # Clean up dead gateway if present
            if gw is not None:
                await self._kill_gateway(user_id, gw)

            # Allocate port and spawn
            port = self._next_port
            self._next_port += 1
            gw = await self._spawn_gateway(profile, port)
            self._gateways[user_id] = gw
            logger.info(f"Gateway spawned for user={user_id} profile={profile} on port={port}")
            return port

    async def _spawn_gateway(self, profile: str, port: int) -> Gateway:
        """Spawn a hermes gateway process and wait for it to become healthy."""
        env = os.environ.copy()
        env["API_SERVER_PORT"] = str(port)

        proc = await asyncio.create_subprocess_exec(
            "hermes", "-p", profile, "gateway", "run",
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        gw = Gateway(port=port, process=proc)

        # Wait for gateway to be healthy
        deadline = time.monotonic() + STARTUP_GRACE_PERIOD
        while time.monotonic() < deadline:
            if await self._is_healthy(gw):
                return gw
            await asyncio.sleep(0.5)

        # Gateway didn't become healthy in time — read stderr for diagnostics
        stderr_data = b""
        try:
            stderr_data = await asyncio.wait_for(proc.stderr.read(), timeout=2.0) if proc.stderr else b""
        except asyncio.TimeoutError:
            pass

        logger.error(
            f"Gateway for profile={profile} on port={port} failed to become healthy "
            f"within {STARTUP_GRACE_PERIOD}s. Stderr: {stderr_data.decode(errors='replace')[:500]}"
        )
        await self._kill_gateway("unknown", gw)
        raise RuntimeError(f"Gateway for profile {profile} failed to start on port {port}")

    async def _is_healthy(self, gw: Gateway) -> bool:
        """Check if a gateway is responding to health checks."""
        if gw.process.returncode is not None:
            return False

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{gw.base_url}/health",
                    timeout=HEALTH_CHECK_TIMEOUT,
                )
            return resp.status_code == 200
        except Exception:
            return False

    async def _kill_gateway(self, user_id: str, gw: Gateway) -> None:
        """Kill a gateway process and clean up."""
        try:
            gw.process.terminate()
            try:
                await asyncio.wait_for(gw.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                gw.process.kill()
                await gw.process.wait()
        except ProcessLookupError:
            pass  # Already dead
        except Exception as e:
            logger.warning(f"Error killing gateway for user={user_id}: {e}")

    async def _reaper_loop(self) -> None:
        """Background loop that kills idle gateways every 60 seconds."""
        while True:
            await asyncio.sleep(60)
            for user_id, gw in list(self._gateways.items()):
                if gw.idle_seconds > IDLE_TIMEOUT_SECONDS:
                    logger.info(
                        f"Reaping idle gateway for user={user_id} "
                        f"(idle {gw.idle_seconds:.0f}s)"
                    )
                    await self._kill_gateway(user_id, gw)
                    del self._gateways[user_id]


# Singleton instance
gateway_manager = GatewayManager()
