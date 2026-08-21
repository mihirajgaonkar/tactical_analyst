export type Competition = {
  id: string;
  name: string;
  country?: string | null;
  gender?: string | null;
};

export type Season = {
  id: string;
  competition_id: string;
  name: string;
};

export type Team = {
  id: string;
  name: string;
  country?: string | null;
};

export type Match = {
  id: string;
  competition_id: string;
  season_id: string;
  kickoff_at?: string | null;
  home_team: Team | null;
  away_team: Team | null;
  home_score?: number | null;
  away_score?: number | null;
  status: string;
};

export type Metric = {
  id: string;
  match_id: string;
  entity_type: string;
  entity_id: string | null;
  metric_name: string;
  metric_version: string;
  value_numeric?: number | null;
  value_json?: Record<string, unknown> | null;
  sample_size?: number | null;
  source_event_ids: string[];
};

export type ReportClaim = {
  id: string;
  claim_text: string;
  claim_type: string;
  strength: "weak" | "moderate" | "strong";
  verification_status: string;
  evidence_ids: string[];
  caveats: string[];
};

export type EvidenceMetric = {
  evidence_id: string;
  metric: string;
  entity_id?: string | null;
  value?: number | Record<string, unknown> | null;
  definition_version: string;
  source_event_ids: string[];
};

export type TacticalReport = {
  id: string;
  match_id: string;
  report_markdown: string;
  verification_status: string;
  evidence_hash: string;
  claims: ReportClaim[];
};

export type JobResponse = {
  job_id: string;
  status: string;
};
