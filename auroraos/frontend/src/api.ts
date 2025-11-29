// frontend/src/api.ts
// AuroraOS — Backend API Client

import type { ContentItem, DecisionPayload, VibeState } from "./types";

// In production (via Vite proxy) or dev, use relative path
const API_BASE = import.meta.env.VITE_AURORA_API_BASE ?? "/v1";

export async function fetchPendingContent(): Promise<ContentItem[]> {
  const res = await fetch(`${API_BASE}/content/pending`);
  if (!res.ok) throw new Error("Failed to fetch pending content");
  return res.json();
}

export async function sendDecision(
  contentId: number,
  payload: DecisionPayload
): Promise<void> {
  const res = await fetch(`${API_BASE}/content/${contentId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Decision failed: ${txt}`);
  }
}

export async function generateBatch(
  type: string = "post",
  targetChannel: string = "instagram"
): Promise<{ content_item_id: number }> {
  const res = await fetch(`${API_BASE}/ai/generate_batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, target_channel: targetChannel }),
  });
  if (!res.ok) throw new Error("Failed to generate batch");
  return res.json();
}

export async function updateVibe(vibe: VibeState): Promise<void> {
  const res = await fetch(`${API_BASE}/ai/vibe/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vibe),
  });
  if (!res.ok) throw new Error("Failed to update vibe");
}

// ═══════════════════════════════════════════════════════════════════
// Analytics API
// ═══════════════════════════════════════════════════════════════════

export interface AnalyticsSummary {
  total_decisions: number;
  total_content: number;
  decision_counts: { decision: string; count: number }[];
  vibe_decision_counts: { vibe_mode: string | null; decision: string; count: number }[];
  strong_feedback: { feedback_type: string; count: number }[];
  rating_distribution: { rating: number; count: number }[];
}

export interface VibePerformance {
  vibe_performance: Record<string, {
    approvals: number;
    rejections: number;
    total: number;
    approval_rate: number;
    strong_positive: number;
    strong_negative: number;
  }>;
  best_vibe: string | null;
}

export async function fetchAnalytics(): Promise<AnalyticsSummary> {
  const res = await fetch(`${API_BASE}/analytics/summary`);
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return res.json();
}

export async function fetchVibePerformance(): Promise<VibePerformance> {
  const res = await fetch(`${API_BASE}/analytics/vibe-performance`);
  if (!res.ok) throw new Error("Failed to fetch vibe performance");
  return res.json();
}

