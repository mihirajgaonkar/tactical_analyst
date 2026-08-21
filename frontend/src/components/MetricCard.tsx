type Props = {
  label: string;
  value: string | number;
  suffix?: string;
};

export function MetricCard({ label, value, suffix }: Props) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>
        {value}
        {suffix ? <small>{suffix}</small> : null}
      </strong>
    </div>
  );
}
