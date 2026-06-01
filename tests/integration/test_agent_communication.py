"""Integration tests for agent communication — HandoverManifest, BaseAgent, AgentRegistry."""

import pytest
from agents.base import BaseAgent
from agents.registry import registry
from app.schemas.agent import HandoverManifest


class TestHandoverManifest:
    """HandoverManifest is the standard inter-agent message format."""

    def test_default_construction(self):
        manifest = HandoverManifest()
        assert manifest.facts == []
        assert manifest.pending_questions == []
        assert manifest.risk_flags == []
        assert manifest.evidence_level == "C"
        assert manifest.context == {}

    def test_full_construction(self):
        manifest = HandoverManifest(
            facts=["Symptom: headache", "Duration: 2 days"],
            pending_questions=["Pain severity?"],
            risk_flags=[],
            evidence_level="B",
            context={"department": "neurology"},
        )
        assert len(manifest.facts) == 2
        assert manifest.evidence_level == "B"
        assert manifest.context["department"] == "neurology"

    def test_evidence_level_default(self):
        """Default evidence level is 'C' (LLM-generated)."""
        manifest = HandoverManifest(facts=["test"])
        assert manifest.evidence_level == "C"


class TestBaseAgent:
    """BaseAgent abstract class provides the agent contract."""

    def test_agent_name_and_tools(self):
        class SimpleAgent(BaseAgent):
            async def run(self, context):
                return HandoverManifest(facts=["processed"])

        agent = SimpleAgent("test_agent")
        assert agent.name == "test_agent"
        assert agent.tools == {}

    async def test_hooks_return_unchanged_by_default(self):
        class SimpleAgent(BaseAgent):
            async def run(self, context):
                return HandoverManifest(facts=["processed"])

        agent = SimpleAgent("hook_test")

        # Pre-process hook returns context unchanged
        ctx = {"key": "value"}
        result = await agent.on_pre_process(ctx)
        assert result == ctx

        # Post-process hook returns manifest unchanged
        manifest = HandoverManifest(facts=["test"])
        result = await agent.on_post_process(manifest)
        assert result == manifest

    def test_tool_registration(self):
        class SimpleAgent(BaseAgent):
            async def run(self, context):
                return HandoverManifest(facts=["processed"])

        agent = SimpleAgent("tool_test")

        def my_tool(x: int) -> int:
            return x * 2

        agent.register_tool("double", my_tool)
        assert "double" in agent.tools

    def test_abstract_cannot_instantiate(self):
        """BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent("bad")  # type: ignore


class TestAgentRegistry:
    """AgentRegistry maintains a global mapping of agent types."""

    def test_register_and_create(self):
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_registry")

            async def run(self, context):
                return HandoverManifest(facts=["from test_registry"])

        registry.register(TestAgent)
        cls = registry.get("test_registry")
        assert cls is TestAgent

        agent = registry.create("test_registry")
        assert agent.name == "test_registry"

    def test_list_registered(self):
        # Import ensures TriageAgent's @registry.register fires
        import agents.triage.agent  # noqa: F401
        agents = registry.list_agents()
        assert "triage" in agents

    def test_get_nonexistent(self):
        with pytest.raises(KeyError):
            registry.get("nonexistent_agent")


class TestAgentCommunicationProtocol:
    """End-to-end agent communication via HandoverManifest."""

    @pytest.mark.asyncio
    async def test_agent_to_manifest_roundtrip(self):
        """Simulate an agent receiving context and producing a manifest."""
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__("test_roundtrip")

            async def run(self, context):
                symptoms = context.get("symptoms", "")
                return HandoverManifest(
                    facts=[f"Analyzed: {symptoms}"],
                    pending_questions=["Duration?"],
                    risk_flags=[],
                    context={"processed": True},
                )

        agent = TestAgent()
        manifest = await agent.run({"symptoms": "cough"})
        assert "cough" in manifest.facts[0]
        assert manifest.context["processed"] is True
