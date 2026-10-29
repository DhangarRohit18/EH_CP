"""
WebGuard Real-Time Server-Sent Events (SSE) Stream
Broadcasts live analysis completions, provider telemetry, and threat events to dashboard.
"""

import json
import asyncio
from typing import AsyncGenerator, Set, Any, Optional
from fastapi import APIRouter
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/events", tags=["Real-Time Telemetry"])

class EventBroadcaster:
    def __init__(self):
        self._queues: Set[asyncio.Queue] = set()

    def register(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=100)
        self._queues.add(q)
        return q

    def unregister(self, q: asyncio.Queue):
        self._queues.discard(q)

    async def broadcast(self, event_type_or_payload: Any, data: Optional[dict] = None):
        if isinstance(event_type_or_payload, dict):
            event_type = event_type_or_payload.get("type", "EVENT")
            payload_data = event_type_or_payload.get("data", event_type_or_payload)
        else:
            event_type = str(event_type_or_payload)
            payload_data = data or {}

        dead_queues = set()
        for q in self._queues:
            try:
                q.put_nowait({"event": event_type, "data": payload_data})
            except asyncio.QueueFull:
                dead_queues.add(q)
        for q in dead_queues:
            self._queues.discard(q)

broadcaster = EventBroadcaster()
event_broadcaster = broadcaster

async def event_generator(client_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    # Send initial connection acknowledgment
    yield f"event: connected\ndata: {json.dumps({'message': 'WebGuard real-time telemetry stream active'})}\n\n"
    try:
        while True:
            try:
                # Wait for next event with a 20s heartbeat keep-alive
                item = await asyncio.wait_for(client_queue.get(), timeout=20.0)
                event_name = item.get("event", "message")
                payload = json.dumps(item.get("data", {}))
                yield f"event: {event_name}\ndata: {payload}\n\n"
            except asyncio.TimeoutError:
                # Heartbeat keep-alive to keep connection open across firewalls
                yield ": heartbeat\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        broadcaster.unregister(client_queue)

@router.get("", response_class=StreamingResponse)
async def subscribe_telemetry():
    """
    Subscribes to live SSE stream for analysis completions and threat telemetry.
    """
    client_q = broadcaster.register()
    return StreamingResponse(
        event_generator(client_q),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
