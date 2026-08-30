"""Patient-facing narration of agent manifests.

Agents emit a structured ``HandoverManifest`` (bullet facts plus a JSON
payload). That structure is what downstream agents and the review/summary
pages need, but it is not what a patient should read, and it arrives all at
once.

Previously the WebSocket faked a typing effect by slicing the rendered bullet
list and sleeping 12ms between slices. This module replaces that with real
streaming: the LLM renders the manifest into patient-friendly prose over its
native streaming API, and each delta is forwarded to the client as it arrives.

Cost note: narration is one additional LLM call per agent stage. It is
controlled by ``MEDINEXUS_STREAM_NARRATIVE`` and degrades to a single
non-simulated message when the LLM or streaming is unavailable.
"""

import inspect
import json
import logging

from app.schemas.agent import HandoverManifest

logger = logging.getLogger(__name__)

NARRATIVE_SYSTEM_PROMPT = """你是一名医生，正在对患者口述刚才的诊疗结论。

要求：
1. 用**自然连贯的中文段落**复述下面的结构化诊疗结果，不要输出任何 JSON、不要使用代码块。
2. 保留全部关键事实：诊断/分诊结论、用药与用法、需要注意的风险、还需要追问的信息。
3. 语气平和、通俗易懂，避免堆砌术语；遇到术语要用一句话解释。
4. 不要新增结构化结果里没有的医学结论、剂量或检查项目。
5. 若结果中包含紧急标记，必须把"立即就医/拨打120"放在开头并明确强调。
6. 结尾附一行简短的免责声明。
7. 全文控制在 300 字以内。"""


def render_manifest(manifest: HandoverManifest) -> str:
    """Render a manifest as the plain bullet list used when not narrating."""
    lines = [f"• {fact}" for fact in manifest.facts]
    if manifest.pending_questions:
        lines.extend(["", "**需要进一步了解:**", *[f"- {q}" for q in manifest.pending_questions]])
    if manifest.risk_flags:
        lines.extend(["", "**⚠ 注意:**", *[f"- {flag}" for flag in manifest.risk_flags]])
    return "\n".join(lines)


def build_narrative_messages(manifest: HandoverManifest) -> list[dict]:
    """Compose the chat messages for the narration call."""
    payload = {
        "facts": manifest.facts,
        "pending_questions": manifest.pending_questions,
        "risk_flags": manifest.risk_flags,
        "evidence_level": manifest.evidence_level,
        "context": manifest.context,
    }
    return [
        {"role": "system", "content": NARRATIVE_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


async def stream_narrative(llm, manifest: HandoverManifest, emit) -> str:
    """Stream the narrated manifest, forwarding real LLM deltas via ``emit``.

    ``emit`` may be sync or async (the WebSocket emitter is async).

    Returns the full narrated text, or ``""`` if streaming produced nothing —
    the caller then falls back to ``render_manifest``.
    """
    collected: list[str] = []
    try:
        async for delta in llm.chat_stream(build_narrative_messages(manifest)):
            if not delta:
                continue
            collected.append(delta)
            result = emit(delta)
            if inspect.isawaitable(result):
                await result
    except Exception as e:  # noqa: BLE001 - narration is cosmetic, never fatal
        logger.warning("Narration streaming failed: %s", e)

    return "".join(collected).strip()
