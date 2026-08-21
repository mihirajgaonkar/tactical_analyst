import Plot from "react-plotly.js";

type Props = {
  labels: string[];
  home: number[];
  away: number[];
  homeName: string;
  awayName: string;
};

export function MetricBars({ labels, home, away, homeName, awayName }: Props) {
  return (
    <Plot
      data={[
        { type: "bar", name: homeName, x: labels, y: home, marker: { color: "#2563eb" } },
        { type: "bar", name: awayName, x: labels, y: away, marker: { color: "#c2410c" } }
      ]}
      layout={{
        autosize: true,
        height: 260,
        margin: { l: 34, r: 10, t: 12, b: 62 },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
        font: { family: "Inter, system-ui, sans-serif", size: 11, color: "#334155" },
        legend: { orientation: "h", x: 0, y: 1.15 }
      }}
      config={{ displayModeBar: false, responsive: true }}
      className="plot"
    />
  );
}
