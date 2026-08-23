import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";

vi.mock("./api/client", async () => {
  const demo = await import("./api/demoData");
  return {
    fetchCompetitions: () => Promise.resolve(demo.demoCompetitions),
    fetchSeasons: (competitionId: string | null) =>
      Promise.resolve(competitionId ? demo.demoSeasons[competitionId] ?? [] : []),
    fetchMatches: (competitionId: string | null, seasonId: string | null) =>
      Promise.resolve(
        demo.demoMatches.filter(
          (match) =>
            match.competition_id === competitionId && match.season_id === seasonId
        )
      ),
    fetchMetrics: (matchId: string | null) =>
      Promise.resolve(matchId ? demo.demoMetrics[matchId] ?? [] : []),
    fetchReport: (matchId: string | null) =>
      Promise.resolve(matchId ? demo.demoReports[matchId] ?? null : null),
    fetchEvidence: (_reportId: string | null, matchId: string | null) =>
      Promise.resolve(matchId ? demo.demoEvidence[matchId] ?? [] : []),
    analyzeMatch: (matchId: string) =>
      Promise.resolve({ job_id: `demo-${matchId}`, status: "queued" }),
    waitForJob: (jobId: string) =>
      Promise.resolve({ job_id: jobId, status: "success", result: { status: "completed" } }),
    ingestMatch: vi.fn(),
    fetchMatch: vi.fn()
  };
});

function renderApp() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } }
  });
  return render(
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>
  );
}

describe("App", () => {
  it("supports match selection, analysis submission, report rendering, and evidence drawer", async () => {
    const user = userEvent.setup();
    renderApp();

    await screen.findByRole("option", { name: "StatsBomb Open Demo" });
    await user.selectOptions(screen.getByLabelText("Competition"), "competition:demo");
    await screen.findByRole("option", { name: "Portfolio Sample" });
    await user.selectOptions(screen.getByLabelText("Season"), "season:demo");
    await user.click(await screen.findByRole("button", { name: /Home FC/i }));

    expect(screen.getByRole("heading", { name: /Home FC vs Away FC/i })).toBeInTheDocument();
    expect(screen.getByText("Analysis Dashboard")).toBeInTheDocument();
    expect(screen.getAllByTestId("plotly-chart").length).toBeGreaterThan(0);

    await user.click(screen.getByRole("button", { name: /Analyze Match/i }));
    await waitFor(() => expect(screen.getByText(/Analysis complete/i)).toBeInTheDocument());

    expect(screen.getByText(/Home FC created the stronger chance profile/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /territory/i }));
    expect(screen.getByRole("heading", { name: "territory" })).toBeInTheDocument();
    expect(screen.getByText("METRIC_FIELD_TILT_TEAM_HOME")).toBeInTheDocument();
  });

  it("shows an empty state before a match is selected", async () => {
    renderApp();

    expect(await screen.findByRole("heading", { name: /Select a completed match/i })).toBeInTheDocument();
    expect(screen.getByText(/Choose a competition, season, and completed match/i)).toBeInTheDocument();
  });
});
