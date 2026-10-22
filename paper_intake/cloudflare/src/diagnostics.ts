import type { FailureCategory, JobRecord } from "./types";

export const ERROR_RETRY_POLICY: Readonly<Record<string, { category: FailureCategory; retryable: boolean }>> = {
  tls_interrupted: { category: "network", retryable: true }, timeout: { category: "network", retryable: true },
  mineru_5xx: { category: "provider", retryable: true }, deepseek_429: { category: "provider", retryable: true },
  mineru_request_failed: { category: "provider", retryable: true }, mineru_parse_failed: { category: "provider", retryable: false },
  deepseek_auth_rejected: { category: "auth", retryable: false }, deepseek_balance_low: { category: "provider", retryable: false },
  deepseek_rate_limited: { category: "provider", retryable: true }, deepseek_unreachable: { category: "network", retryable: true },
  deepseek_request_failed: { category: "provider", retryable: true }, notion_request_failed: { category: "provider", retryable: true },
  arxiv_metadata_failed: { category: "provider", retryable: true },
  deepseek_failed: { category: "provider", retryable: true }, pdf_url_malformed: { category: "validation", retryable: false },
  schema_invalid: { category: "validation", retryable: false }, deepseek_schema_invalid: { category: "validation", retryable: false },
  notion_schema_incompatible: { category: "config", retryable: false }, auth_missing: { category: "config", retryable: false },
  file_io_error: { category: "internal", retryable: false }, processing_failed: { category: "internal", retryable: false },
  retry_exhausted: { category: "internal", retryable: false },
  failed: { category: "internal", retryable: true }, parse_failed: { category: "provider", retryable: true },
  github_dispatch_failed: { category: "publication", retryable: true }, deploy_failed: { category: "publication", retryable: true },
};

export function retryPolicy(code: string | null, fallback = false) {
  return code ? (ERROR_RETRY_POLICY[code] ?? { category: "internal" as const, retryable: fallback }) : { category: "internal" as const, retryable: false };
}

export function sanitizeDiagnostic(value: string): string {
  return value
    .replace(/https?:\/\/[^\s"']+/giu, (url) => {
      try {
        const parsed = new URL(url);
        if (parsed.search) parsed.search = "?[REDACTED]";
        return parsed.toString();
      } catch {
        return "[REDACTED_URL]";
      }
    })
    .replace(/authorization\s*:\s*[^\s,;]+(?:\s+[^\s,;]+)?/giu, "[REDACTED_CREDENTIAL]")
    .replace(/bearer\s+[A-Za-z0-9._~+\/-]+/giu, "[REDACTED_CREDENTIAL]")
    .replace(/\b(?:token|password|secret)\s*=\s*[^\s&,;]+/giu, "[REDACTED_CREDENTIAL]");
}

type EventRecord = { event_type?: unknown; details?: unknown; created_at?: unknown };
function object(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

export function checkpointTitle(checkpoints: Record<string, unknown>): string | null {
  const metadata = object(object(checkpoints.resolve_metadata).metadata);
  const nested = typeof metadata.title === "string" ? metadata.title.trim() : "";
  const legacy = typeof checkpoints.title === "string" ? checkpoints.title.trim() : "";
  return nested || legacy || null;
}

export function computeDiagnosis(job: JobRecord, events: EventRecord[]) {
  const failure = [...events].reverse().find((event) => event.event_type === "job.stage_failed" || event.event_type === "publication.failed");
  const details = object(failure?.details);
  const firstStarted = events.find((event) => event.event_type === "job.stage_started");
  const queueDurationMs = firstStarted && typeof firstStarted.created_at === "string" ? Math.max(0, Date.parse(firstStarted.created_at) - Date.parse(job.createdAt)) : null;
  const durations = Object.entries(stageMetrics(events)).flatMap(([stage, data]) =>
    typeof data.duration_ms === "number" ? [{ stage, duration: data.duration_ms }] : [],
  ).sort((a, b) => b.duration - a.duration);
  const exhausted = events.some((event) => event.event_type === "job.retry_exhausted");
  const policy = retryPolicy(typeof details.code === "string" ? details.code : job.errorCode, Boolean(details.retryable));
  return {
    result: job.status === "failed" ? "failed" : job.status === "published" ? "success" : "in_progress",
    total_duration_ms: Math.max(0, Date.parse(job.updatedAt) - Date.parse(job.createdAt)), queue_duration_ms: queueDurationMs,
    bottleneck: durations[0]?.stage ?? null, bottleneck_duration_ms: durations[0]?.duration ?? null,
    failed_stage: typeof details.stage === "string" ? details.stage : null,
    root_cause: typeof details.code === "string" ? details.code : job.errorCode,
    next_action: typeof details.diagnostic_hint === "string" ? details.diagnostic_hint : null,
    retryable: exhausted ? false : policy.retryable,
  };
}

export function stageMetrics(events: EventRecord[]): Record<string, Record<string, unknown>> {
  const result: Record<string, Record<string, unknown>> = {};
  const started: Record<string, number> = {};
  for (const event of events) {
    const details = object(event.details);
    if (typeof details.stage !== "string") continue;
    if (event.event_type === "job.stage_started" && typeof event.created_at === "string") {
      started[details.stage] = Date.parse(event.created_at);
    }
    if (event.event_type === "job.stage_completed") {
      const completedAt = typeof event.created_at === "string" ? Date.parse(event.created_at) : Number.NaN;
      const duration = typeof details.duration_ms === "number"
        ? details.duration_ms
        : Number.isFinite(completedAt) && Number.isFinite(started[details.stage])
          ? Math.max(0, completedAt - started[details.stage])
          : null;
      result[details.stage] = { ...details, duration_ms: duration };
    }
  }
  return result;
}
