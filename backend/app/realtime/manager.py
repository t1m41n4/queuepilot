from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.observability import log_event, metrics


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, branch_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[branch_id].add(websocket)
        metrics.increment("websocket_connections_total")
        metrics.increment("websocket_connections_active")
        log_event("websocket_connected", branch_id=branch_id)

    def disconnect(self, branch_id: int, websocket: WebSocket) -> None:
        connections = self._connections.get(branch_id)
        if connections is None:
            return
        was_connected = websocket in connections
        connections.discard(websocket)
        if not was_connected:
            return
        metrics.increment("websocket_disconnections_total")
        metrics.increment("websocket_connections_active", -1)
        log_event("websocket_disconnected", branch_id=branch_id)
        if not connections:
            self._connections.pop(branch_id, None)

    async def broadcast(self, branch_id: int, message: dict[str, object]) -> None:
        for websocket in list(self._connections.get(branch_id, ())):
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(branch_id, websocket)
                metrics.increment("websocket_broadcast_errors_total")
                log_event("websocket_broadcast_failed", level=30, branch_id=branch_id)


connection_manager = ConnectionManager()
