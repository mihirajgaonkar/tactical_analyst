import ReactMarkdown from "react-markdown";
import { ExternalLink } from "lucide-react";
import type { ReportClaim, TacticalReport } from "../types";

type Props = {
  report: TacticalReport | null | undefined;
  loading: boolean;
  onClaimSelect: (claim: ReportClaim) => void;
};

export function TacticalReportPanel({ report, loading, onClaimSelect }: Props) {
  if (loading) {
    return <div className="report-loading">Loading report</div>;
  }
  if (!report) {
    return <div className="report-loading">No verified report available yet.</div>;
  }
  return (
    <div className="report-layout">
      <article className="markdown">
        <ReactMarkdown>{report.report_markdown}</ReactMarkdown>
      </article>
      <div className="claims-list">
        {report.claims.map((claim) => (
          <button key={claim.id} className="claim-button" onClick={() => onClaimSelect(claim)}>
            <span>{claim.strength}</span>
            <b>{claim.claim_type}</b>
            <small>{claim.claim_text}</small>
            <ExternalLink size={15} />
          </button>
        ))}
      </div>
    </div>
  );
}
