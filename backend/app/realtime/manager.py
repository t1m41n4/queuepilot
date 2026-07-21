from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, branch_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[branch_id].add(websocket)

    def disconnect(self, branch_id: int, websocket: WebSocket) -> None:
        connections = self._connections.get(branch_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(branch_id, None)

    async def broadcast(self, branch_id: int, message: dict[str, object]) -> None:
        for websocket in list(self._connections.get(branch_id, ())):
            try:
                await websocket.send_json(message)
            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(branch_id, websocket)


connection_manager = ConnectionManager()
