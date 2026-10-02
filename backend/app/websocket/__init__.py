"""VisionTrack ANPR — WebSocket Connection Manager."""

from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket
from app.core.logging import get_logger

logger = get_logger("websocket")


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}  # channel -> connections
        self._all_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, channel: str = "default"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        self._all_connections.append(websocket)
        logger.info("ws_connected", channel=channel, total=len(self._all_connections))

    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
            except ValueError:
                pass
        try:
            self._all_connections.remove(websocket)
        except ValueError:
            pass
        logger.info("ws_disconnected", channel=channel, total=len(self._all_connections))

    async def broadcast(self, message: dict[str, Any], channel: str = "default"):
        """Broadcast a message to all connections on a channel."""
        connections = self.active_connections.get(channel, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, channel)

    async def broadcast_all(self, message: dict[str, Any]):
        """Broadcast to all connections regardless of channel."""
        dead = []
        for ws in self._all_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            for channel in self.active_connections:
                try:
                    self.active_connections[channel].remove(ws)
                except ValueError:
                    pass
            try:
                self._all_connections.remove(ws)
            except ValueError:
                pass

    @property
    def connection_count(self) -> int:
        return len(self._all_connections)


ws_manager = ConnectionManager()
