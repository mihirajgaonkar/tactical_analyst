import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

afterEach(() => cleanup());

vi.mock("react-plotly.js", () => ({
  default: ({ className }: { className?: string }) => (
    <div className={className} data-testid="plotly-chart" />
  )
}));
