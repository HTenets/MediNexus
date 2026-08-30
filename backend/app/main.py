"""MediNexus FastAPI application entry point."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from app.api.router import api_router
from app.core.database import db_enabled, engine
from app.core.demo_seed import seed_demo_data
from app.core.rag import set_rag_query
from app.config import settings
from app.middlewares.auth import auth_middleware
from app.middlewares.rate_limit import rate_limit_middleware
from knowledge.factory import create_rag_query
from llm.factory import create_llm_client
from orchestration.narrative import render_manifest, stream_narrative
from orchestration.supervisor import supervisor
from orchestration.stream import StreamManager

# Build the LLM client once at startup. If no provider/key is configured the
# agent pipeline automatically degrades to rule-based mode.
llm_client = create_llm_client()

# Build the retrieval stack once: BM25 over the bundled knowledge base, with
# Qdrant as the vector route when configured. Injected into the supervisor so
# agents get real retrieval instead of a keyword lookup over seed strings.
rag_query = create_rag_query()
set_rag_query(rag_query)
supervisor.rag_query = rag_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Max user message length to prevent abuse
MAX_MESSAGE_LENGTH = 5000


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not db_enabled():
        logger.info("🔧 No DATABASE_URL configured — running without persistence (demo).")
    elif settings.demo_mode:
        await seed_demo_data()
        logger.info("🔧 DEMO MODE: database connected, demo accounts/data seeded.")
    else:
        logger.info("🚀 PRODUCTION MODE: database connected.")
    yield
    if db_enabled():
        await engine.dispose()


app = FastAPI(title="MediNexus", version="0.1.1", lifespan=lifespan)

origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()] if settings.allowed_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware — always enabled to prevent abuse
app.middleware("http")(rate_limit_middleware)

# Authentication middleware
app.middleware("http")(auth_middleware)

# REST API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def root_health():
    return {"status": "ok"}


def _verify_ws_token(token: str | None) -> str | None:
    """Validate a JWT access token for WebSocket connections. Returns user_id or None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None


async def _run_agent_stream(session, stream, content: str, llm_client=None) -> bool:
    """Run the current agent stage and stream its output. Returns True on success."""
    agent_name = session.current_agent
    await stream.emit_agent_start(agent_name)

    try:
        manifest = await supervisor.run_agent(
            session, content, llm_client=llm_client
        )
    except Exception:
        logger.exception("Agent processing error for session %s", session.session_id)
        await stream.emit_error("处理过程中发生错误，请重试", "AGENT_ERROR")
        return False

    summary_text = await _emit_summary(manifest, stream, llm_client, agent_name)

    await stream.emit_agent_end(
        summary=summary_text,
        manifest=manifest.model_dump(),
    )
    return True


async def _emit_summary(manifest, stream, llm, agent_name: str) -> str:
    """Send the stage result to the client, streaming it when possible.

    With an LLM configured the manifest is narrated into patient-friendly
    prose over the provider's real streaming API, so tokens arrive as the model
    produces them. Without one, the rendered manifest is sent in a single
    message — never sliced up with artificial sleeps to look like typing.
    """
    if llm is not None and settings.stream_narrative:
        narrated = await stream_narrative(llm, manifest, stream.emit_token)
        if narrated:
            return narrated
        logger.info("Narration empty for agent %s — sending rendered manifest", agent_name)

    text = render_manifest(manifest)
    if text:
        await stream.emit_token(text)
    return text


async def _run_finalize(session, stream, llm_client=None) -> None:
    """Auto-run the remaining pipeline stages (review → followup) to finalize."""
    # Accumulate all user-described symptoms so later agents have full context.
    symptoms = " ".join(
        h.get("content", "") for h in session.history if h.get("role") == "user"
    ).strip()

    ran_any = False
    for _ in range(6):
        if session.current_agent in ("complete", "emergency_protocol"):
            break
        ok = await _run_agent_stream(session, stream, symptoms, llm_client)
        ran_any = True
        if not ok:
            break
        if session.current_agent == "emergency_protocol":
            await stream.emit_info(
                "已启动紧急预案，请立即拨打 120 或前往最近的急诊。"
            )
            break

    if session.current_agent == "complete":
        await stream.emit_info("诊疗方案已生成，问诊结束。")
    elif session.current_agent != "emergency_protocol":
        await stream.emit_info("问诊已结束，如需重新开始请新建会话。")

    # Ensure the client always receives a terminal agent_end so its
    # processing indicator resets (e.g. when nothing ran because the
    # pipeline was already finished).
    if not ran_any:
        await stream.emit_agent_end(summary="", manifest={})


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str | None = Query(default=None),
):
    """WebSocket endpoint for streaming consultation dialogue.

    Authentication: pass a valid access token via the `token` query parameter.

    Message protocol (client → server):
        {"type": "message", "content": "I have a headache"}

    Event protocol (server → client):
        {"event": "agent_start",  "data": {"agent": "triage", ...}}
        {"event": "token",        "data": {"token": "..."}}
        {"event": "agent_end",    "data": {"summary": "...", "manifest": {...}}}
        {"event": "error",        "data": {"message": "...", "code": "..."}}
        {"event": "info",         "data": {"message": "..."}}
    """
    # Authenticate before accepting the connection
    user_id = _verify_ws_token(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    stream = StreamManager(websocket.send_text)

    session = await supervisor.get_session(session_id)
    if not session:
        session = await supervisor.create_session(
            session_id, f"patient_{session_id[:8]}", owner_id=user_id
        )
    elif session.owner_id and session.owner_id != user_id:
        # Session belongs to another user — reject to prevent unauthorized
        # access to another patient's consultation history (IDOR).
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await stream.emit_info("欢迎使用医枢智能问诊。请描述您的症状。")

    # Observability: make degraded (rule-based) mode explicit to the user
    # instead of silently returning templated answers.
    if llm_client is None:
        await stream.emit_info(
            "提示：当前未配置大模型，正在使用规则引擎降级模式，回复为模板内容。"
        )

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

            # Keep-alive heartbeat from the client. Reply with a pong so the
            # client's stale-connection timer resets. Never treated as a message.
            if msg_type == "ping":
                await stream.send_event("pong", {})
                continue

            # "生成诊疗方案": auto-run the remaining pipeline stages
            # (review → followup) to produce the full plan without requiring
            # further user text.
            if msg_type == "finalize":
                await _run_finalize(session, stream, llm_client)
                continue

            if msg_type != "message" or not content.strip():
                await stream.emit_error("消息内容不能为空", "EMPTY_MESSAGE")
                continue

            if len(content) > MAX_MESSAGE_LENGTH:
                await stream.emit_error(
                    f"消息过长，请限制在{MAX_MESSAGE_LENGTH}字以内", "MESSAGE_TOO_LONG"
                )
                continue

            # Run the CURRENT agent stage for this message. The pipeline
            # advances one stage per message (triage → doctor → review →
            # followup) so the user interacts with each agent in turn.
            if session.current_agent in ("complete", "emergency_protocol"):
                if session.current_agent == "emergency_protocol":
                    await stream.emit_info("紧急预案已启动，请立即拨打 120 或前往最近的急诊。")
                else:
                    await stream.emit_info("问诊已结束，如需重新开始请新建会话。")
                continue

            await _run_agent_stream(session, stream, content, llm_client)

            if session.current_agent == "emergency_protocol":
                await stream.emit_info("紧急预案已启动，请立即拨打 120 或前往最近的急诊。")

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
    except Exception:
        logger.exception("WebSocket error for session %s", session_id)
