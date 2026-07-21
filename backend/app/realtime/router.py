from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.manager import connection_manager


router = APIRouter()


@router.websocket("/ws/queue/{branch_id}")
async def queue_websocket(websocket: WebSocket, branch_id: int) -> None:
    await connection_manager.connect(branch_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(branch_id, websocket)
