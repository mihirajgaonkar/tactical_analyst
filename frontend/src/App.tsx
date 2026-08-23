import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  BarChart3,
  FileText,
  Gauge,
  Goal,
  Layers3,
  Play,
  Shield,
  Users
} from "lucide-react";
import {
  analyzeMatch,
  fetchCompetitions,
  fetchEvidence,
  fetchMatch,
  fetchMatches,
  fetchMetrics,
  fetchReport,
  fetchSeasons,
  ingestMatch,
  waitForJob
} from "./api/client";
import { MetricCard } from "./components/MetricCard";
import { Section } from "./components/Section";
import { EvidenceDrawer } from "./components/EvidenceDrawer";
import { MatchExplorer } from "./pages/MatchExplorer";
import { MetricBars } from "./charts/MetricBars";
import { XgTimeline } from "./charts/XgTimeline";
import { TacticalReportPanel } from "./pages/TacticalReportPanel";
import type { EvidenceMetric, Match, Metric, ReportClaim } from "./types";
import { findTeamMetric, metricNumber, metricValue } from "./utils/metrics";

export function App() {
  const queryClient = useQueryClient();
  const [competitionId, setCompetitionId] = useState<string | null>(null);
  const [seasonId, setSeasonId] = useState<string | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [activeClaim, setActiveClaim] = useState<ReportClaim | null>(null);

  const competitions = useQuery({ queryKey: ["competitions"], queryFn: fetchCompetitions });
  const seasons = useQuery({
    queryKey: ["seasons", competitionId],
    queryFn: () => fetchSeasons(competitionId)
  });
  const matches = useQuery({
    queryKey: ["matches", competitionId, seasonId],
    queryFn: () => fetchMatches(competitionId, seasonId)
  });
  const metrics = useQuery({
    queryKey: ["metrics", selectedMatch?.id],
    queryFn: () => fetchMetrics(selectedMatch?.id ?? null)
  });
  const report = useQuery({
    queryKey: ["report", selectedMatch?.id],
    queryFn: () => fetchReport(selectedMatch?.id ?? null)
  });
  const evidence = useQuery({
    queryKey: ["evidence", report.data?.id, selectedMatch?.id],
    queryFn: () => fetchEvidence(report.data?.id ?? null, selectedMatch?.id ?? null)
  });
  const importMatchMutation = useMutation({
    mutationFn: async (providerMatchId: string) => {
      const queued = await ingestMatch(providerMatchId);
      const completed = await waitForJob(queued.job_id);
      const result = typeof completed.result === "object" ? completed.result : null;
      const matchId = result?.match_id;
      if (!matchId) throw new Error("Ingestion completed without returning a match ID");
      return fetchMatch(matchId);
    },
    onSuccess: async (match) => {
      setCompetitionId(match.competition_id);
      setSeasonId(match.season_id);
      setSelectedMatch(match);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["competitions"] }),
        queryClient.invalidateQueries({ queryKey: ["seasons", match.competition_id] }),
        queryClient.invalidateQueries({ queryKey: ["matches", match.competition_id, match.season_id] })
      ]);
    }
  });
  const analyze = useMutation({
    mutationFn: async (matchId: string) => {
      const queued = await analyzeMatch(matchId);
      return waitForJob(queued.job_id);
    },
    onSuccess: async (_job, matchId) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["metrics", matchId] }),
        queryClient.invalidateQueries({ queryKey: ["report", matchId] })
      ]);
    }
  });

  const homeId = selectedMatch?.home_team?.id ?? "";
  const awayId = selectedMatch?.away_team?.id ?? "";
  const summary = useMemo(
    () => buildSummary(metrics.data ?? [], homeId, awayId),
    [metrics.data, homeId, awayId]
  );

  const activeEvidence = useMemo(
    () => evidenceForClaim(activeClaim, evidence.data ?? []),
    [activeClaim, evidence.data]
  );

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Goal size={22} />
          <div>
            <strong>Tactical Analyst</strong>
            <span>StatsBomb Open Data MVP</span>
          </div>
        </div>
        <MatchExplorer
          competitions={competitions.data ?? []}
          seasons={seasons.data ?? []}
          matches={matches.data ?? []}
          selectedCompetitionId={competitionId}
          selectedSeasonId={seasonId}
          selectedMatchId={selectedMatch?.id ?? null}
          loading={competitions.isLoading || seasons.isLoading || matches.isLoading}
          onCompetitionChange={(id) => {
            setCompetitionId(id);
            setSeasonId(null);
            setSelectedMatch(null);
          }}
          onSeasonChange={(id) => {
            setSeasonId(id);
            setSelectedMatch(null);
          }}
          onMatchSelect={(match) => {
            setSelectedMatch(match);
            setActiveClaim(null);
            analyze.reset();
          }}
          onAnalyze={(match) => analyze.mutate(match.id)}
          analyzeStatus={
            analyze.isPending
              ? "running"
              : analyze.isError
                ? "failed"
                : analyze.isSuccess
                  ? "completed"
                  : null
          }
          analyzeError={analyze.isError ? errorMessage(analyze.error) : null}
          importStatus={
            importMatchMutation.isPending
              ? "running"
              : importMatchMutation.isSuccess
                ? "completed"
                : null
          }
          importError={
            importMatchMutation.isError ? errorMessage(importMatchMutation.error) : null
          }
          onImport={(providerMatchId) => importMatchMutation.mutate(providerMatchId)}
        />
      </aside>

      <section className="workspace">
        <header className="match-header">
          <div>
            <span className="eyebrow">Analysis Dashboard</span>
            <h1>{selectedMatch ? matchTitle(selectedMatch) : "Select a completed match"}</h1>
          </div>
          {selectedMatch ? (
            <div className="scoreline">
              <span>{selectedMatch.home_score ?? "-"}</span>
              <small>FT</small>
              <span>{selectedMatch.away_score ?? "-"}</span>
            </div>
          ) : null}
        </header>

        {selectedMatch ? (
          <div className="dashboard-grid">
            <Section title="Overview" icon={<Activity size={18} />}>
              <div className="metric-grid">
                <MetricCard label="Home xG" value={summary.homeXg} />
                <MetricCard label="Away xG" value={summary.awayXg} />
                <MetricCard label="Field Tilt" value={summary.fieldTilt} suffix="%" />
                <MetricCard label="Shots" value={summary.shots} />
              </div>
              <XgTimeline home={summary.homeXgNumber} away={summary.awayXgNumber} />
            </Section>

            <Section title="Territory & Progression" icon={<Layers3 size={18} />}>
              <MetricBars
                labels={["Progressive Passes", "Box Entries", "Field Tilt"]}
                home={[summary.homeProgressivePasses, summary.homeBoxEntries, summary.homeFieldTilt]}
                away={[summary.awayProgressivePasses, summary.awayBoxEntries, summary.awayFieldTilt]}
                homeName={selectedMatch.home_team?.name ?? "Home"}
                awayName={selectedMatch.away_team?.name ?? "Away"}
              />
            </Section>

            <Section title="Pressing & Defending" icon={<Shield size={18} />}>
              <div className="metric-grid">
                <MetricCard label="Home PPDA" value={summary.homePpda} />
                <MetricCard label="Away PPDA" value={summary.awayPpda} />
                <MetricCard label="Home High Turnovers" value={summary.homeHighTurnovers} />
                <MetricCard label="Away High Turnovers" value={summary.awayHighTurnovers} />
              </div>
            </Section>

            <Section title="Build-Up" icon={<BarChart3 size={18} />}>
              <div className="visual-placeholder" aria-label="Passing network visualization">
                <span>Passing Network</span>
                <div className="network-node n1" />
                <div className="network-node n2" />
                <div className="network-node n3" />
                <div className="network-edge e1" />
                <div className="network-edge e2" />
              </div>
            </Section>

            <Section title="Players" icon={<Users size={18} />}>
              <div className="table-like">
                <span>Feature</span>
                <span>Leader</span>
                <span>Evidence</span>
                <b>Progression</b>
                <span>{selectedMatch.home_team?.name}</span>
                <span>{summary.homeProgressivePasses} progressive passes</span>
                <b>Chance quality</b>
                <span>{selectedMatch.home_team?.name}</span>
                <span>{summary.homeXg} xG</span>
              </div>
            </Section>

            <Section title="Substitutions" icon={<Gauge size={18} />}>
              <div className="timeline">
                <span>Pre-window</span>
                <div />
                <strong>Substitution</strong>
                <div />
                <span>Post-window</span>
              </div>
            </Section>

            <Section title="Tactical Report" icon={<FileText size={18} />} wide>
              <TacticalReportPanel
                report={report.data}
                loading={report.isLoading || analyze.isPending}
                onClaimSelect={setActiveClaim}
              />
            </Section>
          </div>
        ) : (
          <div className="empty-state">
            <Play size={24} />
            <p>Choose a competition, season, and completed match to inspect deterministic metrics.</p>
          </div>
        )}
      </section>

      <EvidenceDrawer
        claim={activeClaim}
        evidence={activeEvidence}
        onClose={() => setActiveClaim(null)}
      />
    </main>
  );
}

function matchTitle(match: Match) {
  return `${match.home_team?.name ?? "Home"} vs ${match.away_team?.name ?? "Away"}`;
}

function buildSummary(metrics: Metric[], homeId: string, awayId: string) {
  const homeXg = findTeamMetric(metrics, "xg", homeId);
  const awayXg = findTeamMetric(metrics, "xg", awayId);
  const homeShots = findTeamMetric(metrics, "shots", homeId);
  const awayShots = findTeamMetric(metrics, "shots", awayId);
  const homeFieldTilt = metricNumber(findTeamMetric(metrics, "field_tilt", homeId)) * 100;
  const awayFieldTilt = metricNumber(findTeamMetric(metrics, "field_tilt", awayId)) * 100;
  return {
    homeXg: metricValue(homeXg),
    awayXg: metricValue(awayXg),
    homeXgNumber: metricNumber(homeXg),
    awayXgNumber: metricNumber(awayXg),
    shots: `${jsonNumber(homeShots, "shots")} - ${jsonNumber(awayShots, "shots")}`,
    fieldTilt: Math.round(homeFieldTilt),
    homeFieldTilt,
    awayFieldTilt,
    homePpda: metricValue(findTeamMetric(metrics, "ppda", homeId)),
    awayPpda: metricValue(findTeamMetric(metrics, "ppda", awayId)),
    homeProgressivePasses: metricNumber(findTeamMetric(metrics, "progressive_passes", homeId)),
    awayProgressivePasses: metricNumber(findTeamMetric(metrics, "progressive_passes", awayId)),
    homeBoxEntries: metricNumber(findTeamMetric(metrics, "box_entries", homeId)),
    awayBoxEntries: metricNumber(findTeamMetric(metrics, "box_entries", awayId)),
    homeHighTurnovers: metricValue(findTeamMetric(metrics, "high_turnovers", homeId)),
    awayHighTurnovers: metricValue(findTeamMetric(metrics, "high_turnovers", awayId))
  };
}

function jsonNumber(metric: Metric | undefined, key: string) {
  const value = metric?.value_json?.[key];
  return typeof value === "number" ? value : 0;
}

function evidenceForClaim(claim: ReportClaim | null, evidence: EvidenceMetric[]) {
  if (!claim) return [];
  return evidence.filter((item) => claim.evidence_ids.includes(item.evidence_id));
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Unexpected error";
}
