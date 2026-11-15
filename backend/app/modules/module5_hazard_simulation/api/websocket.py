import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.modules.module5_hazard_simulation.services.websocket_manager import ws_manager
from app.modules.module5_hazard_simulation.api.endpoints import controller

logger = logging.getLogger("SimulationWebSocket")

ws_router = APIRouter()

@ws_router.websocket("/ws/simulations/{session_id}")
async def simulation_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Real-time bi-directional WebSocket interface for simulation telemetry streaming."""
    await ws_manager.connect(session_id, websocket)
    try:
        # Send initial session snapshot upon connection
        session = controller.get_session(session_id)
        if session:
            await websocket.send_text(json.dumps({
                "type": "SESSION_SNAPSHOT",
                "session": session.to_response().model_dump(mode="json"),
                "latest_reading": session.latest_reading.model_dump(mode="json") if session.latest_reading else None
            }))

        while True:
            data_text = await websocket.receive_text()
            try:
                cmd = json.loads(data_text)
                action = cmd.get("action", "").lower()
                
                if action == "step":
                    reading = controller.step_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "SIMULATION_STEP",
                        "reading": reading.model_dump(mode="json"),
                        "session": session.to_response().model_dump(mode="json")
                    })
                elif action == "start":
                    controller.start_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "STATUS_CHANGED",
                        "status": "RUNNING",
                        "session": session.to_response().model_dump(mode="json")
                    })
                elif action == "pause":
                    controller.pause_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "STATUS_CHANGED",
                        "status": "PAUSED",
                        "session": session.to_response().model_dump(mode="json")
                    })
                elif action == "resume":
                    controller.resume_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "STATUS_CHANGED",
                        "status": "RUNNING",
                        "session": session.to_response().model_dump(mode="json")
                    })
                elif action == "stop":
                    controller.stop_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "STATUS_CHANGED",
                        "status": "STOPPED",
                        "session": session.to_response().model_dump(mode="json")
                    })
                elif action == "reset":
                    controller.reset_session(session_id)
                    await ws_manager.broadcast(session_id, {
                        "type": "STATUS_CHANGED",
                        "status": "IDLE",
                        "session": session.to_response().model_dump(mode="json")
                    })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({"type": "ERROR", "message": str(e)}))

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)

