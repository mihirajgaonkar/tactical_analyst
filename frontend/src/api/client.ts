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

async function requiredJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
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

export function fetchMatch(matchId: string) {
  return requiredJson<Match>(`/matches/${encodeURIComponent(matchId)}`);
}

export function ingestMatch(providerMatchId: string) {
  return requiredJson<JobResponse>(
    `/matches/${encodeURIComponent(providerMatchId.trim())}/ingest`,
    { method: "POST" }
  );
}

export function analyzeMatch(matchId: string) {
  if (matchId === "match:demo") {
    return Promise.resolve<JobResponse>({ job_id: `demo-${matchId}`, status: "queued" });
  }
  return requiredJson<JobResponse>(`/matches/${encodeURIComponent(matchId)}/analyze`, {
    method: "POST"
  });
}

export async function waitForJob(
  jobId: string,
  timeoutMs = 300_000,
  pollIntervalMs = 1_000
): Promise<JobResponse> {
  if (jobId.startsWith("demo-")) {
    return { job_id: jobId, status: "success", result: { status: "completed" } };
  }
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const job = await requiredJson<JobResponse>(`/jobs/${encodeURIComponent(jobId)}`);
    if (job.status === "success") {
      if (typeof job.result === "object" && job.result?.status === "failed_verification") {
        throw new Error(job.result.errors?.join("; ") || "Report verification failed");
      }
      return job;
    }
    if (["failure", "revoked"].includes(job.status)) {
      const detail = typeof job.result === "string" ? job.result : `Job ${job.status}`;
      throw new Error(detail);
    }
    await new Promise((resolve) => window.setTimeout(resolve, pollIntervalMs));
  }
  throw new Error("The job did not finish within five minutes");
}

export function fetchReport(matchId: string | null) {
  if (!matchId) return Promise.resolve<TacticalReport | null>(null);
  return getJson<TacticalReport | null>(
    `/matches/${encodeURIComponent(matchId)}/report`,
    demoReports[matchId] ?? null
  );
}

export async function fetchEvidence(reportId: string | null, matchId: string | null) {
  if (!reportId || !matchId) return [];
  const fallback = { metrics: demoEvidence[matchId] ?? [] };
  const evidence = await getJson<{ metrics?: EvidenceMetric[] }>(
    `/reports/${encodeURIComponent(reportId)}/evidence`,
    fallback
  );
  return evidence.metrics ?? [];
}
