from __future__ import annotations

from tactical_analyst.analytics.base import MatchContext, MetricCalculator
from tactical_analyst.analytics.passing import PassingMetrics
from tactical_analyst.analytics.players import PlayerMetrics
from tactical_analyst.analytics.possession import PossessionMetrics
from tactical_analyst.analytics.pressing import PressingMetrics
from tactical_analyst.analytics.progression import ProgressionMetrics
from tactical_analyst.analytics.shots import ShotMetrics
from tactical_analyst.analytics.spatial import SpatialMetrics
from tactical_analyst.analytics.substitutions import SubstitutionMetrics
from tactical_analyst.analytics.territory import TerritoryMetrics
from tactical_analyst.analytics.transitions import TransitionMetrics
from tactical_analyst.schemas.metric import MetricResult

METRIC_REGISTRY: dict[str, MetricCalculator] = {
    "shots": ShotMetrics(),
    "passing": PassingMetrics(),
    "progression": ProgressionMetrics(),
    "territory": TerritoryMetrics(),
    "pressing": PressingMetrics(),
    "possession": PossessionMetrics(),
    "transitions": TransitionMetrics(),
    "spatial": SpatialMetrics(),
    "players": PlayerMetrics(),
    "substitutions": SubstitutionMetrics(),
}


def calculate_all_metrics(
    context: MatchContext,
    registry: dict[str, MetricCalculator] | None = None,
) -> list[MetricResult]:
    """Calculate every registered metric in deterministic registry order."""

    calculators = registry or METRIC_REGISTRY
    results: list[MetricResult] = []
    for calculator in calculators.values():
        results.extend(calculator.calculate(context))
    return results
