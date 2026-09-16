import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger("allstreak.websocket")

class ConnectionManager:
    def __init__(self):
        # Map workspace_id -> set of active WebSockets
        self.active_workspace_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.active_workspace_connections:
            self.active_workspace_connections[workspace_id] = set()
        self.active_workspace_connections[workspace_id].add(websocket)
        logger.info(f"WebSocket client connected for workspace {workspace_id}")

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.active_workspace_connections:
            self.active_workspace_connections[workspace_id].discard(websocket)
            if not self.active_workspace_connections[workspace_id]:
                del self.active_workspace_connections[workspace_id]
        logger.info(f"WebSocket client disconnected for workspace {workspace_id}")

    async def broadcast_to_workspace(self, workspace_id: str, event_type: str, data: Any):
        if workspace_id not in self.active_workspace_connections:
            return

        payload = json.dumps({
            "event": event_type,
            "data": data
        })

        disconnected = set()
        for connection in self.active_workspace_connections[workspace_id]:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)

        for dead in disconnected:
            self.disconnect(dead, workspace_id)

ws_manager = ConnectionManager()
