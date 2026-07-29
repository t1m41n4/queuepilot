from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.manager import connection_manager
from app.core.observability import log_event


router = APIRouter()


@router.websocket("/ws/queue/{branch_id}")
async def queue_websocket(websocket: WebSocket, branch_id: int) -> None:
    await connection_manager.connect(branch_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(branch_id, websocket)
    except Exception:
        connection_manager.disconnect(branch_id, websocket)
        log_event("websocket_error", level=40, branch_id=branch_id)
        raise
