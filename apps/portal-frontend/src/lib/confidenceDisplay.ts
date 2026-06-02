import { asMetadata, type SubmitResponse } from "./submitResponse";

function finiteNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(String(value).trim());
  return Number.isFinite(n) ? n : null;
}

/** SSOT fallback chain for operator confidence display (Sprint 5E). */
export function resolveOperationalConfidence(
  response: SubmitResponse | null | undefined,
): number | null {
  if (!response) return null;

  const metadata = asMetadata(response);
  const topLevel = finiteNumber(response.confidence);
  if (topLevel !== null && topLevel > 0) return topLevel;

  const mlConfidence = finiteNumber(metadata?.ml_confidence);
  if (mlConfidence !== null) return mlConfidence;

  const scoreConfidence = finiteNumber(metadata?.confidence_score);
  if (scoreConfidence !== null) return scoreConfidence;

  return topLevel;
}
