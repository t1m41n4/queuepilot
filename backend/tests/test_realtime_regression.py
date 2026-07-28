import unittest

from app.realtime.manager import ConnectionManager


class _WebSocket:
    def __init__(self):
        self.messages = []

    async def send_json(self, message):
        self.messages.append(message)

    async def accept(self):
        pass


class RealtimeRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_broadcast_delivers_to_branch_connections(self):
        manager = ConnectionManager()
        websocket = _WebSocket()
        await manager.connect(7, websocket)
        message = {"event": "QUEUE_UPDATED", "branch_id": 7, "queue_id": 3, "state": {"status": "READY"}}
        await manager.broadcast(7, message)
        self.assertEqual(websocket.messages, [message])
        manager.disconnect(7, websocket)
        self.assertNotIn(7, manager._connections)


if __name__ == "__main__":
    unittest.main()
