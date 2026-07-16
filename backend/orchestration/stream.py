"""Streaming event handling and SSE formatting for agent output."""

import json
import logging
from typing import Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# SSE event type constants
class StreamEvent:
    AGENT_START = "agent_start"
    TOKEN = "token"
    AGENT_END = "agent_end"
    ERROR = "error"
    INFO = "info"
    STATE_UPDATE = "state_update"


@dataclass
class StreamEventData:
    """Represents a single streaming event to be sent to the client."""
    event: str
    data: dict[str, Any] = field(default_factory=dict)


def format_sse(event: str, data: dict) -> str:
    """Format an SSE message string.

    Format:
      event: <event_type>\n
      data: <json_payload>\n\n
    """
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def format_ws_message(event: str, data: dict) -> str:
    """Format a JSON message for WebSocket transmission.

    WebSocket messages use a simple JSON envelope:
    {"event": "token", "data": {"token": "..."}}
    """
    return json.dumps({"event": event, "data": data}, ensure_ascii=False)


class StreamManager:
    """Manages streaming of agent output through WebSocket connections.

    Provides helper methods to emit typed events during agent execution.
    """

    def __init__(self, send_fn: callable):
        """
        send_fn: an async callable that accepts a string message to send.
        For WebSocket, this is `websocket.send_text()`.
        """
        self._send = send_fn
        self._current_agent: str | None = None

    async def send_event(self, event: str, data: dict[str, Any]):
        """Send a JSON event through the WebSocket."""
        try:
            await self._send(format_ws_message(event, data))
        except Exception as e:
            logger.warning("Stream send failed: %s", e)

    async def emit_agent_start(self, agent: str, metadata: dict[str, Any] | None = None):
        """Notify client that an agent has started processing."""
        self._current_agent = agent
        from datetime import datetime, timezone
        await self.send_event(StreamEvent.AGENT_START, {
            "agent": agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        })

    async def emit_token(self, token: str):
        """Stream a single token (word or character) to the client."""
        if token:
            await self.send_event(StreamEvent.TOKEN, {"token": token})

    async def emit_agent_end(self, summary: str = "", manifest: dict | None = None):
        """Notify client that the current agent has finished."""
        await self.send_event(StreamEvent.AGENT_END, {
            "agent": self._current_agent or "",
            "summary": summary,
            "manifest": manifest or {},
        })
        self._current_agent = None

    async def emit_error(self, message: str, code: str = "INTERNAL_ERROR"):
        """Send an error event to the client."""
        logger.error("Stream error [%s]: %s", code, message)
        await self.send_event(StreamEvent.ERROR, {
            "message": message,
            "code": code,
        })

    async def emit_info(self, message: str):
        """Send an informational message."""
        await self.send_event(StreamEvent.INFO, {"message": message})

    async def emit_state_update(self, key: str, value: Any):
        """Send a state update (e.g., triage result, department assignment)."""
        await self.send_event(StreamEvent.STATE_UPDATE, {key: value})

    async def stream_agent_response(self, agent_name: str, response_iterator: AsyncGenerator[str, None], manifest: dict | None = None):
        """Convenience: emit agent_start → tokens → agent_end from an async generator."""
        await self.emit_agent_start(agent_name)
        full_text = ""
        async for token in response_iterator:
            full_text += token
            await self.emit_token(token)
        await self.emit_agent_end(summary=full_text, manifest=manifest)


def create_sse_event_generator(stream_mgr: StreamManager) -> AsyncGenerator[str, None]:
    """Create an SSE-formatted async generator from a StreamManager.

    This adapter converts StreamManager events to SSE format for
    use with FastAPI's StreamingResponse (SSE over HTTP).
    """
    # This is a placeholder for HTTP-based SSE fallback
    # The primary mode uses WebSocket JSON messages
    async def _generate():
        # This would yield SSE-formatted strings based on a queue
        yield format_sse(StreamEvent.INFO, {"message": "SSE stream active"})
    return _generate()
