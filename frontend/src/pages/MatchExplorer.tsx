import { Calendar, Play, RefreshCw } from "lucide-react";
import type { Competition, Match, Season } from "../types";

type Props = {
  competitions: Competition[];
  seasons: Season[];
  matches: Match[];
  selectedCompetitionId: string | null;
  selectedSeasonId: string | null;
  selectedMatchId: string | null;
  loading: boolean;
  analyzeStatus: string | null;
  onCompetitionChange: (id: string) => void;
  onSeasonChange: (id: string) => void;
  onMatchSelect: (match: Match) => void;
  onAnalyze: (match: Match) => void;
};

export function MatchExplorer({
  competitions,
  seasons,
  matches,
  selectedCompetitionId,
  selectedSeasonId,
  selectedMatchId,
  loading,
  analyzeStatus,
  onCompetitionChange,
  onSeasonChange,
  onMatchSelect,
  onAnalyze
}: Props) {
  const selectedMatch = matches.find((match) => match.id === selectedMatchId) ?? null;

  return (
    <div className="explorer">
      <label>
        Competition
        <select
          value={selectedCompetitionId ?? ""}
          onChange={(event) => onCompetitionChange(event.target.value)}
        >
          <option value="" disabled>
            Choose competition
          </option>
          {competitions.map((competition) => (
            <option key={competition.id} value={competition.id}>
              {competition.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        Season
        <select
          value={selectedSeasonId ?? ""}
          onChange={(event) => onSeasonChange(event.target.value)}
          disabled={!selectedCompetitionId}
        >
          <option value="" disabled>
            Choose season
          </option>
          {seasons.map((season) => (
            <option key={season.id} value={season.id}>
              {season.name}
            </option>
          ))}
        </select>
      </label>

      <div className="match-list" aria-label="Match selection">
        <div className="list-title">
          <Calendar size={16} />
          <span>Completed Matches</span>
          {loading ? <RefreshCw size={14} className="spin" /> : null}
        </div>
        {matches.map((match) => (
          <button
            key={match.id}
            className={match.id === selectedMatchId ? "match-row selected" : "match-row"}
            onClick={() => onMatchSelect(match)}
          >
            <span>{match.home_team?.name}</span>
            <b>
              {match.home_score ?? "-"}-{match.away_score ?? "-"}
            </b>
            <span>{match.away_team?.name}</span>
          </button>
        ))}
      </div>

      <button
        className="primary-button"
        disabled={!selectedMatch}
        onClick={() => selectedMatch && onAnalyze(selectedMatch)}
      >
        <Play size={17} />
        {analyzeStatus ? `Analysis ${analyzeStatus}` : "Analyze Match"}
      </button>
    </div>
  );
}
