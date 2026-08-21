import Plot from "react-plotly.js";

type Props = {
  home: number;
  away: number;
};

export function XgTimeline({ home, away }: Props) {
  const data = [
    {
      type: "scatter",
      mode: "lines+markers",
      name: "Home",
      x: [0, 18, 44, 67, 90],
      y: [0, home * 0.18, home * 0.42, home * 0.71, home],
      line: { color: "#2563eb", shape: "hv" }
    },
    {
      type: "scatter",
      mode: "lines+markers",
      name: "Away",
      x: [0, 25, 52, 78, 90],
      y: [0, away * 0.2, away * 0.48, away * 0.8, away],
      line: { color: "#c2410c", shape: "hv" }
    }
  ];

  return (
    <Plot
      data={data as never}
      layout={{
        autosize: true,
        height: 230,
        margin: { l: 36, r: 10, t: 10, b: 32 },
        xaxis: { title: { text: "Minute" } },
        yaxis: { title: { text: "xG" } },
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
