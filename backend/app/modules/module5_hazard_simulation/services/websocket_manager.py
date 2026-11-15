import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("SimulationWebSocketManager")

class SimulationWebSocketManager:
    """Manages real-time WebSocket client connections and simulation event broadcasting."""

    def __init__(self):
        # Maps session_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket client connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}")

    async def broadcast(self, session_id: str, message: dict):
        if session_id not in self.active_connections:
            return
        dead_connections = []
        payload = json.dumps(message)
        for conn in self.active_connections[session_id]:
            try:
                await conn.send_text(payload)
            except Exception as e:
                logger.warning(f"Failed to send to client in session {session_id}: {e}")
                dead_connections.append(conn)

        for dead in dead_connections:
            self.disconnect(session_id, dead)

ws_manager = SimulationWebSocketManager()

