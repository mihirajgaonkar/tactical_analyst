import type {
  Competition,
  EvidenceMetric,
  JobResponse,
  Match,
  Metric,
  Season,
  TacticalReport
} from "../types";
import {
  demoCompetitions,
  demoEvidence,
  demoMatches,
  demoMetrics,
  demoReports,
  demoSeasons
} from "./demoData";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

async function postJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { method: "POST" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function fetchCompetitions() {
  return getJson<Competition[]>("/competitions", demoCompetitions);
}

export function fetchSeasons(competitionId: string | null) {
  if (!competitionId) return Promise.resolve<Season[]>([]);
  return getJson<Season[]>(`/competitions/${competitionId}/seasons`, demoSeasons[competitionId] ?? []);
}

export function fetchMatches(competitionId: string | null, seasonId: string | null) {
  if (!competitionId || !seasonId) return Promise.resolve<Match[]>([]);
  const fallback = demoMatches.filter(
    (match) => match.competition_id === competitionId && match.season_id === seasonId
  );
  return getJson<Match[]>(
    `/matches?competition_id=${encodeURIComponent(competitionId)}&season_id=${encodeURIComponent(seasonId)}`,
    fallback
  );
}

export function fetchMetrics(matchId: string | null) {
  if (!matchId) return Promise.resolve<Metric[]>([]);
  return getJson<Metric[]>(`/matches/${matchId}/metrics`, demoMetrics[matchId] ?? []);
}

export function analyzeMatch(matchId: string) {
  return postJson<JobResponse>(`/matches/${matchId}/analyze`, {
    job_id: `demo-${matchId}`,
    status: "queued"
  });
}

export function fetchReport(matchId: string | null) {
  if (!matchId) return Promise.resolve<TacticalReport | null>(null);
  return Promise.resolve(demoReports[matchId] ?? null);
}

export function fetchEvidence(matchId: string | null) {
  if (!matchId) return Promise.resolve<EvidenceMetric[]>([]);
  return Promise.resolve(demoEvidence[matchId] ?? []);
}
