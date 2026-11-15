import asyncio
import json
from typing import Set
from fastapi import WebSocket

class ConnectionManager:
    """Manages active WebSocket connections for real-time mission telemetry updates."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def broadcast_sync(self, message: dict):
        """Dispatches real-time telemetry updates to connected WebSockets if server event loop is active."""
        if not self.active_connections:
            return
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._send_all(message))
        except RuntimeError:
            # No running event loop (e.g. during standalone test execution)
            pass

    async def _send_all(self, message: dict):
        dead_connections = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                dead_connections.add(connection)
        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)

connection_manager = ConnectionManager()
