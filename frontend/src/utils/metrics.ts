import type { Metric } from "../types";

export function findTeamMetric(metrics: Metric[], name: string, teamId: string) {
  return metrics.find((metric) => metric.metric_name === name && metric.entity_id === teamId);
}

export function metricNumber(metric?: Metric) {
  if (!metric) return 0;
  if (typeof metric.value_numeric === "number") return metric.value_numeric;
  return 0;
}

export function metricValue(metric?: Metric) {
  if (!metric) return "0";
  if (typeof metric.value_numeric === "number") return formatNumber(metric.value_numeric);
  return "detail";
}

export function formatNumber(value: number) {
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}
