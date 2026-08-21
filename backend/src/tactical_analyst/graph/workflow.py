from __future__ import annotations

from tactical_analyst.graph.nodes import (
    build_evidence_packet_node,
    final_numeric_verification_node,
    final_report_node,
    persist_report_node,
    repair_claims_node,
    tactical_interpretation_node,
    validate_match_node,
    verify_claims_node,
)
from tactical_analyst.graph.routing import route_after_verification


class TacticalAnalysisWorkflow:
    """Small orchestration wrapper matching the planned LangGraph node order."""

    def __init__(self, llm_service, max_repair_attempts: int = 1) -> None:
        self.llm_service = llm_service
        self.max_repair_attempts = max_repair_attempts

    def run(self, state: dict) -> dict:
        state = validate_match_node(state)
        if state.get("errors"):
            return state
        state = build_evidence_packet_node(state)
        state = tactical_interpretation_node(state, self.llm_service)
        while True:
            state = verify_claims_node(state)
            route = route_after_verification(state)
            if route == "valid":
                break
            if route == "invalid":
                return state
            state = repair_claims_node(state, self.llm_service, self.max_repair_attempts)
        state = final_report_node(state, self.llm_service)
        state = final_numeric_verification_node(state)
        if state.get("verification_errors"):
            return state
        return persist_report_node(state)


def build_langgraph_workflow(llm_service):
    """Build a LangGraph workflow when langgraph is installed."""

    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install langgraph to build the LangGraph workflow") from exc

    from tactical_analyst.graph.state import TacticalAnalysisState

    graph = StateGraph(TacticalAnalysisState)
    graph.add_node("validate_match", validate_match_node)
    graph.add_node("build_evidence_packet", build_evidence_packet_node)
    graph.add_node(
        "tactical_interpretation_llm",
        lambda state: tactical_interpretation_node(state, llm_service),
    )
    graph.add_node("verify_claims", verify_claims_node)
    graph.add_node("repair_claims", lambda state: repair_claims_node(state, llm_service))
    graph.add_node("final_report_llm", lambda state: final_report_node(state, llm_service))
    graph.add_node("final_numeric_verification", final_numeric_verification_node)
    graph.add_node("persist_report", persist_report_node)
    graph.add_edge(START, "validate_match")
    graph.add_edge("validate_match", "build_evidence_packet")
    graph.add_edge("build_evidence_packet", "tactical_interpretation_llm")
    graph.add_edge("tactical_interpretation_llm", "verify_claims")
    graph.add_conditional_edges(
        "verify_claims",
        route_after_verification,
        {"valid": "final_report_llm", "repair": "repair_claims", "invalid": END},
    )
    graph.add_edge("repair_claims", "verify_claims")
    graph.add_edge("final_report_llm", "final_numeric_verification")
    graph.add_edge("final_numeric_verification", "persist_report")
    graph.add_edge("persist_report", END)
    return graph.compile()
