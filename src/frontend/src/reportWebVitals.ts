import type { Metric, ReportHandler } from "web-vitals";

const reportWebVitals = (onPerfEntry?: ReportHandler) => {
  if (typeof window === "undefined") return;

  const report: ReportHandler =
    onPerfEntry ??
    ((metric: Metric) => {
      if (import.meta.env.DEV) {
        console.debug(`[perf] ${metric.name}`, Math.round(metric.value));
      }

      window.dispatchEvent(
        new CustomEvent("primeagent:performance", { detail: metric }),
      );
    });

  void import("web-vitals").then(({ onCLS, onFCP, onINP, onLCP, onTTFB }) => {
    onCLS(report);
    onFCP(report);
    onINP(report);
    onLCP(report);
    onTTFB(report);
  });
};

export default reportWebVitals;
