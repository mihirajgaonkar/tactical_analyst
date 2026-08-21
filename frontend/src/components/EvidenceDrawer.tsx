import { X } from "lucide-react";
import type { EvidenceMetric, ReportClaim } from "../types";

type Props = {
  claim: ReportClaim | null;
  evidence: EvidenceMetric[];
  onClose: () => void;
};

export function EvidenceDrawer({ claim, evidence, onClose }: Props) {
  return (
    <aside className={claim ? "drawer open" : "drawer"} aria-hidden={!claim}>
      <button className="icon-button close-button" onClick={onClose} aria-label="Close evidence">
        <X size={18} />
      </button>
      {claim ? (
        <>
          <span className="eyebrow">Evidence</span>
          <h2>{claim.claim_type}</h2>
          <p>{claim.claim_text}</p>
          <div className="evidence-list">
            {evidence.map((item) => (
              <div className="evidence-item" key={item.evidence_id}>
                <strong>{item.metric}</strong>
                <span>{item.evidence_id}</span>
                <b>{formatValue(item.value)}</b>
                <small>{item.definition_version}</small>
              </div>
            ))}
          </div>
          {claim.caveats.length ? (
            <div className="caveats">
              {claim.caveats.map((caveat) => (
                <span key={caveat}>{caveat}</span>
              ))}
            </div>
          ) : null}
        </>
      ) : null}
    </aside>
  );
}

function formatValue(value: EvidenceMetric["value"]) {
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(2);
  if (!value) return "-";
  return JSON.stringify(value);
}
