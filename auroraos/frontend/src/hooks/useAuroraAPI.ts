/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS API Hooks                                             ║
 * ║   Sprint 007: Dashboard Data Fetching                            ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect, useCallback } from "react";

// In production (via Vite proxy) or dev, use relative path
const API_BASE = import.meta.env.VITE_AURORA_API_BASE ?? "/v1";

// ═══════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════

export interface DayEvent {
  id: number;
  time: string;
  tag: string;
  description: string;
  energy: number | null;
  mood: string | null;
}

export interface DayTimeline {
  date: string;
  title: string | null;
  note: string | null;
  events: DayEvent[];
}

export interface DaySummary {
  vibe_summary: string;
  what_happened: string;
  evening_suggestion: string;
  energy_advice: string;
}

export interface DayStats {
  total_days: number;
  total_events: number;
  top_tags: { tag: string; count: number }[];
}

export interface AnalyticsSummary {
  total_content: number;
  total_decisions: number;
  pending_content: number;
  decisions_by_type: { decision: string; count: number }[];
  strong_feedback: { feedback_type: string; count: number }[];
}

export interface EngineStatus {
  engine: string;
  status: string;
  llm_enabled: boolean;
  model: string;
  mode: string;
  capabilities: string[];
  dedicated_to: string;
}

export interface GenerateResult {
  content_item_id: number;
  engine: string;
  variants_count: number;
}

export interface WallItem {
  id: number;
  type: string;
  target_channel: string;
  text: string;
  vibe_mode: string;
  created_at: string;
}

export interface ContentWall {
  items: WallItem[];
  count: number;
}

// ═══════════════════════════════════════════════════════════════════
// API Functions
// ═══════════════════════════════════════════════════════════════════

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// ═══════════════════════════════════════════════════════════════════
// Hooks
// ═══════════════════════════════════════════════════════════════════

export function useTimeline(date?: string) {
  const [data, setData] = useState<DayTimeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const path = date ? `/day/timeline/${date}` : "/day/timeline";
      const result = await fetchJSON<DayTimeline>(path);
      setData(result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [date]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}

export function useDaySummary(date?: string) {
  const [data, setData] = useState<DaySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchJSON<DaySummary>("/ai/day_summary", {
          method: "POST",
          body: JSON.stringify({ date: date || null }),
        });
        setData(result);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [date]);

  return { data, loading, error };
}

export function useDayStats() {
  const [data, setData] = useState<DayStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchJSON<DayStats>("/day/stats");
        setData(result);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return { data, loading, error };
}

export function useAnalytics() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchJSON<AnalyticsSummary>("/analytics/summary");
        setData(result);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return { data, loading, error };
}

// Quick Event Log
export async function logEvent(
  tag: string,
  description: string,
  energy?: number,
  mood?: string
): Promise<DayTimeline> {
  return fetchJSON<DayTimeline>("/day/event", {
    method: "POST",
    body: JSON.stringify({ tag, description, energy, mood }),
  });
}

// ═══════════════════════════════════════════════════════════════════
// Engine Status Hook
// ═══════════════════════════════════════════════════════════════════

export function useEngineStatus() {
  const [data, setData] = useState<EngineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchJSON<EngineStatus>("/ai/status");
        setData(result);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return { data, loading, error };
}

// ═══════════════════════════════════════════════════════════════════
// Quick Generate Content
// ═══════════════════════════════════════════════════════════════════

export async function generateContent(
  scenario: string,
  type: string = "post",
  target_channel: string = "instagram"
): Promise<GenerateResult> {
  return fetchJSON<GenerateResult>("/ai/generate_batch", {
    method: "POST",
    body: JSON.stringify({ type, target_channel, scenario }),
  });
}

// Preset scenarios for quick generation
export const QUICK_SCENARIOS = [
  { id: "morning_coffee", label: "☕ Sabah Kahvesi", icon: "☕" },
  { id: "red_dress_night", label: "👗 Kırmızı Gece", icon: "👗" },
  { id: "street_casual", label: "🚶‍♀️ Sokak Casual", icon: "🚶‍♀️" },
  { id: "gym_lowkey", label: "💪 Spor Vibes", icon: "💪" },
  { id: "pijama_selfie", label: "🌙 Pijama Mood", icon: "🌙" },
] as const;

// ═══════════════════════════════════════════════════════════════════
// Content Wall Hook (Approved Content)
// ═══════════════════════════════════════════════════════════════════

export function useContentWall(limit: number = 20) {
  const [data, setData] = useState<ContentWall | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchJSON<ContentWall>(`/content/wall?limit=${limit}`);
      setData(result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}

