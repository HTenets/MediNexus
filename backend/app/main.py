"""MediNexus FastAPI application entry point."""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.database import engine
from app.config import settings
from app.middlewares.rate_limit import rate_limit_middleware
from orchestration.supervisor import SupervisorAgent
from orchestration.stream import StreamManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global supervisor instance
supervisor = SupervisorAgent()

# Demo mode check
IS_DEMO = settings.demo_mode or not settings.database_url


@asynccontextmanager
async def lifespan(app: FastAPI):
    if IS_DEMO:
        logger.info("🔧 DEMO MODE: Running without database. Data will NOT persist.")
    else:
        logger.info("🚀 PRODUCTION MODE: Database connected.")
    yield
    if not IS_DEMO:
        await engine.dispose()


app = FastAPI(title="MediNexus", version="0.1.0", lifespan=lifespan)

origins = settings.allowed_origins.split(",") if settings.allowed_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (skip in demo mode)
if not IS_DEMO:
    app.middleware("http")(rate_limit_middleware)

# REST API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def root_health():
    return {"status": "ok"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming consultation dialogue.

    Message protocol (client → server):
        {"type": "message", "content": "I have a headache"}

    Event protocol (server → client):
        {"event": "agent_start",  "data": {"agent": "triage", ...}}
        {"event": "token",        "data": {"token": "..."}}
        {"event": "agent_end",    "data": {"summary": "...", "manifest": {...}}}
        {"event": "error",        "data": {"message": "...", "code": "..."}}
        {"event": "info",         "data": {"message": "..."}}
    """
    await websocket.accept()
    stream = StreamManager(websocket.send_text)

    session = supervisor.get_session(session_id)
    if not session:
        session = await supervisor.create_session(session_id, f"patient_{session_id[:8]}")

    await stream.emit_info("欢迎使用医枢智能问诊。请描述您的症状。")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await stream.emit_error("消息格式错误", "INVALID_FORMAT")
                continue

            msg_type = data.get("type", "")
            content = data.get("content", "")

            if msg_type != "message" or not content.strip():
                await stream.emit_error("消息内容不能为空", "EMPTY_MESSAGE")
                continue

            # Process through the agent pipeline
            agent_name = session.current_agent
            await stream.emit_agent_start(agent_name)

            try:
                manifest = await supervisor.run_agent(session, content)

                # Build summary from manifest facts
                lines = []
                for fact in manifest.facts:
                    lines.append(f"• {fact}")
                if manifest.pending_questions:
                    lines.extend(["", "**需要进一步了解:**",
                                   *[f"- {q}" for q in manifest.pending_questions]])
                if manifest.risk_flags:
                    lines.extend(["", "**⚠ 注意:**",
                                   *[f"- {flag}" for flag in manifest.risk_flags]])

                summary_text = "\n".join(lines)

                # Stream token by token for real-time effect
                import asyncio
                for ch in summary_text:
                    await stream.emit_token(ch)
                    await asyncio.sleep(0.01)

                await stream.emit_agent_end(
                    summary=summary_text,
                    manifest=manifest.model_dump(),
                )

            except Exception as e:
                logger.exception("Agent processing error for session %s", session_id)
                await stream.emit_error(f"处理错误: {str(e)}", "AGENT_ERROR")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
    except Exception as e:
        logger.exception("WebSocket error for session %s", session_id)
    finally:
        pass
