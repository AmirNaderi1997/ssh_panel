from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.core.logging import logger
from backend.app.core.security import verify_token

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class ConnectionManager:
    def __init__(self) -> None:
        # channel_name -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {
            "dashboard": [],
            "online_users": [],
            "alerts": []
        }

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """Accept connection and add to channel subscription list."""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info("New WebSocket subscription", channel=channel, active_count=len(self.active_connections[channel]))

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """Remove connection from channel subscription list."""
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
            logger.info("WebSocket subscription ended", channel=channel, active_count=len(self.active_connections[channel]))

    async def send_personal_message(self, message: Any, websocket: WebSocket) -> None:
        """Send message directly to a specific connection."""
        await websocket.send_json(message)

    async def broadcast(self, message: Any, channel: str) -> None:
        """Broadcast message to all subscribers of a channel."""
        if channel not in self.active_connections:
            return
            
        disconnected_sockets = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected_sockets.append(connection)

        # Cleanup failed connections
        for dead_socket in disconnected_sockets:
            self.disconnect(dead_socket, channel)


manager = ConnectionManager()


@router.websocket("/dashboard")
async def websocket_dashboard(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Access Token for authentication")
):
    """WebSocket feed for real-time dashboard CPU/RAM updates and alerts."""
    # Verify token
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001)  # Unauthorized
        return

    await manager.connect(websocket, "dashboard")
    try:
        while True:
            # Maintain connection, handle client pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")


@router.websocket("/online-users")
async def websocket_online_users(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Access Token for authentication")
):
    """WebSocket feed for real-time online tunneling connections."""
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, "online_users")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "online_users")
