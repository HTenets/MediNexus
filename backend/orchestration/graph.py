"""ConsultationGraph — LangGraph-based state graph for the consultation pipeline.

Nodes (agents) registered:
  - triage   → TriageAgent
  - doctor   → DoctorAgent
  - review   → ReviewAgent
  - followup → FollowupAgent
  - coordinator → CoordinatorAgent

Routing after each node is determined by the SupervisorAgent.
"""

from typing import Any, Literal
from langgraph.graph import StateGraph, END
from orchestration.state import GraphState


def _make_router(agent_map: dict[str, str]) -> callable:
    """Factory: builds a conditional edge function from an agent-name map."""
    def router(state: GraphState) -> Literal["doctor", "review", "followup", "coordinator", "__end__"]:
        next_agent = state.get("current_agent", "triage")
        mapped = agent_map.get(next_agent)
        if mapped == "END":
            return "__end__"
        return mapped or "__end__"
    return router


class ConsultationGraph:
    """Builds and exposes the compiled consultation LangGraph."""

    def __init__(self, agent_map: dict[str, str] | None = None):
        """
        agent_map: maps each agent name to the next node.
        Default: triage→doctor, doctor→review, review→END, followup→END.
        Override for multi-specialty / coordinator flows.
        """
        self.agent_map = agent_map or {
            "triage": "doctor",
            "doctor": "review",
            "review": "END",
            "followup": "END",
            "coordinator": "review",
        }
        self.nodes: dict[str, callable] = {}
        self.app = None

    def add_node(self, name: str, fn: callable):
        """Register a node function that processes GraphState."""
        self.nodes[name] = fn

    def build(self) -> StateGraph:
        """Compile the StateGraph with registered nodes and edges."""
        workflow = StateGraph(GraphState)

        for name, fn in self.nodes.items():
            workflow.add_node(name, fn)

        # Set the triage node as the entry point
        workflow.set_entry_point("triage")

        # Conditional edges from every registered node
        router = _make_router(self.agent_map)
        for name in self.nodes:
            workflow.add_conditional_edges(name, router, {
                "doctor": "doctor",
                "review": "review",
                "followup": "followup",
                "coordinator": "coordinator",
                "__end__": END,
            })

        self.app = workflow.compile()
        return self.app

    async def ainvoke(self, initial_state: dict[str, Any]) -> dict[str, Any]:
        """Run the graph asynchronously and return the final state."""
        if self.app is None:
            self.build()
        return await self.app.ainvoke(initial_state)

    async def astream(self, initial_state: dict[str, Any]):
        """Run the graph and yield (node_name, state_update) tuples."""
        if self.app is None:
            self.build()
        async for event in self.app.astream(initial_state):
            yield event
