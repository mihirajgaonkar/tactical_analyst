import type { Competition, EvidenceMetric, Match, Metric, Season, TacticalReport } from "../types";

export const demoCompetitions: Competition[] = [
  { id: "competition:demo", name: "StatsBomb Open Demo", country: "International", gender: "mixed" }
];

export const demoSeasons: Record<string, Season[]> = {
  "competition:demo": [
    { id: "season:demo", competition_id: "competition:demo", name: "Portfolio Sample" }
  ]
};

export const demoMatches: Match[] = [
  {
    id: "match:demo",
    competition_id: "competition:demo",
    season_id: "season:demo",
    kickoff_at: "2024-01-01T15:00:00Z",
    home_team: { id: "team:home", name: "Home FC" },
    away_team: { id: "team:away", name: "Away FC" },
    home_score: 2,
    away_score: 1,
    status: "available"
  }
];

export const demoMetrics: Record<string, Metric[]> = {
  "match:demo": [
    metric("metric:xg:home", "team:home", "xg", 1.86, null, ["s1", "s2", "s3"]),
    metric("metric:xg:away", "team:away", "xg", 0.92, null, ["s4", "s5"]),
    metric("metric:shots:home", "team:home", "shots", null, { shots: 13, goals: 2, xg_per_shot: 0.143 }, ["s1"]),
    metric("metric:shots:away", "team:away", "shots", null, { shots: 8, goals: 1, xg_per_shot: 0.115 }, ["s4"]),
    metric("metric:field:home", "team:home", "field_tilt", 0.62, { numerator: 44, denominator: 71 }, ["p1"]),
    metric("metric:field:away", "team:away", "field_tilt", 0.38, { numerator: 27, denominator: 71 }, ["p2"]),
    metric("metric:ppda:home", "team:home", "ppda", 8.4, null, ["d1", "d2"]),
    metric("metric:ppda:away", "team:away", "ppda", 13.9, null, ["d3"]),
    metric("metric:prog-pass:home", "team:home", "progressive_passes", 41, null, ["p3"]),
    metric("metric:prog-pass:away", "team:away", "progressive_passes", 24, null, ["p4"]),
    metric("metric:box:home", "team:home", "box_entries", 18, { passes: 13, carries: 5 }, ["e1"]),
    metric("metric:box:away", "team:away", "box_entries", 9, { passes: 7, carries: 2 }, ["e2"]),
    metric("metric:turnover:home", "team:home", "high_turnovers", 7, { leading_to_shot: 3, leading_to_goal: 1 }, ["r1"]),
    metric("metric:turnover:away", "team:away", "high_turnovers", 3, { leading_to_shot: 1, leading_to_goal: 0 }, ["r2"])
  ]
};

export const demoEvidence: Record<string, EvidenceMetric[]> = {
  "match:demo": [
    evidence("METRIC_XG_TEAM_HOME", "xg", "team:home", 1.86, ["s1", "s2", "s3"]),
    evidence("METRIC_XG_TEAM_AWAY", "xg", "team:away", 0.92, ["s4", "s5"]),
    evidence("METRIC_FIELD_TILT_TEAM_HOME", "field_tilt", "team:home", 0.62, ["p1"]),
    evidence("METRIC_PPDA_TEAM_HOME", "ppda", "team:home", 8.4, ["d1", "d2"]),
    evidence("METRIC_HIGH_TURNOVERS_TEAM_HOME", "high_turnovers", "team:home", 7, ["r1"]),
    evidence("METRIC_BOX_ENTRIES_TEAM_HOME", "box_entries", "team:home", 18, ["e1"])
  ]
};

export const demoReports: Record<string, TacticalReport> = {
  "match:demo": {
    id: "report:demo",
    match_id: "match:demo",
    evidence_hash: "demo-evidence-hash",
    verification_status: "passed",
    report_markdown:
      "## Match Summary\n\nHome FC created the stronger chance profile and paired it with better territory. Their 1.86 xG and 62% field tilt show a side that reached valuable areas more often without relying only on volume.\n\n## Territory & Pressing\n\nHome FC's lower PPDA and seven high turnovers point to more active pressure. The evidence supports pressure activity and regain outcomes, not a claim about true defensive line height.\n\n## Players & Changes\n\nThe substitution window should be read as a before/after comparison. Attacking output increased after the change, but the report does not claim causality.",
    claims: [
      {
        id: "claim:territory",
        claim_text: "Home FC held the clearer territorial advantage.",
        claim_type: "territory",
        strength: "strong",
        verification_status: "passed",
        evidence_ids: ["METRIC_FIELD_TILT_TEAM_HOME", "METRIC_BOX_ENTRIES_TEAM_HOME"],
        caveats: []
      },
      {
        id: "claim:press",
        claim_text: "Home FC pressed more actively and turned that activity into several high regains.",
        claim_type: "pressing",
        strength: "moderate",
        verification_status: "passed",
        evidence_ids: ["METRIC_PPDA_TEAM_HOME", "METRIC_HIGH_TURNOVERS_TEAM_HOME"],
        caveats: ["Event data supports defensive action height, not true line height."]
      }
    ]
  }
};

function metric(
  id: string,
  entityId: string,
  name: string,
  numeric: number | null,
  json: Record<string, unknown> | null,
  events: string[]
): Metric {
  return {
    id,
    match_id: "match:demo",
    entity_type: "team",
    entity_id: entityId,
    metric_name: name,
    metric_version: `${name}_v1`,
    value_numeric: numeric,
    value_json: json,
    sample_size: events.length,
    source_event_ids: events
  };
}

function evidence(
  evidence_id: string,
  metricName: string,
  entityId: string,
  value: number,
  events: string[]
): EvidenceMetric {
  return {
    evidence_id,
    metric: metricName,
    entity_id: entityId,
    value,
    definition_version: `${metricName}_v1`,
    source_event_ids: events
  };
}
