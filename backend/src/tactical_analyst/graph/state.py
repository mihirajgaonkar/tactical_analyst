from typing import Any, TypedDict


class TacticalAnalysisState(TypedDict, total=False):
    job_id: str
    match_id: str
    provider: str
    provider_capabilities: dict[str, Any]
    match: dict[str, Any]
    match_loaded: bool
    metric_results: list[dict[str, Any]]
    visualization_assets: list[dict[str, Any]]
    evidence_packet: dict[str, Any] | None
    interpretation: dict[str, Any] | None
    verification_errors: list[str]
    verification_attempts: int
    report: dict[str, Any] | None
    report_markdown: str | None
    errors: list[str]
