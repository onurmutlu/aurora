/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS — Story Mode / Timeline Tab                           ║
 * ║   Sprint 007: Visual Dashboard                                   ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import { useState } from "react";
import { colors, gradients, shadows } from "../brand/colors";
import { useTimeline, useDaySummary, logEvent } from "../hooks/useAuroraAPI";
import type { DayEvent } from "../hooks/useAuroraAPI";

// ═══════════════════════════════════════════════════════════════════
// Tag Icons & Colors
// ═══════════════════════════════════════════════════════════════════

const TAG_CONFIG: Record<string, { emoji: string; color: string; label: string }> = {
  walk: { emoji: "🚶", color: "#00F5A0", label: "Walk" },
  gym: { emoji: "💪", color: "#FF6B6B", label: "Gym" },
  yoga: { emoji: "🧘", color: "#B8A7F9", label: "Yoga" },
  starbucks: { emoji: "☕", color: "#00704A", label: "Coffee" },
  coffee: { emoji: "☕", color: "#8B4513", label: "Coffee" },
  lunch: { emoji: "🍽", color: "#FFD93D", label: "Lunch" },
  sugoda: { emoji: "🎙", color: "#AD5FFF", label: "Sugoda" },
  dm: { emoji: "💬", color: "#AFA3FF", label: "DM" },
  work: { emoji: "💼", color: "#CFCFCF", label: "Work" },
  low_energy: { emoji: "🪫", color: "#FF8C42", label: "Low Energy" },
  tired: { emoji: "😴", color: "#6C757D", label: "Tired" },
  happy: { emoji: "😊", color: "#FFD93D", label: "Happy" },
  calm: { emoji: "😌", color: "#00F5A0", label: "Calm" },
  anxious: { emoji: "😰", color: "#FF6B6B", label: "Anxious" },
  creative: { emoji: "✨", color: "#F7D6FF", label: "Creative" },
};

function getTagConfig(tag: string) {
  return TAG_CONFIG[tag.toLowerCase()] || { emoji: "•", color: "#CFCFCF", label: tag };
}

// ═══════════════════════════════════════════════════════════════════
// Event Card Component
// ═══════════════════════════════════════════════════════════════════

function EventCard({ event }: { event: DayEvent }) {
  const config = getTagConfig(event.tag);
  const time = new Date(event.time).toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        padding: "14px 16px",
        background: gradients.cardSurface,
        borderRadius: 12,
        border: `1px solid ${colors.borderSubtle}`,
        marginBottom: 10,
        transition: "all 0.2s ease",
      }}
      className="hover:scale-[1.01]"
    >
      {/* Time */}
      <div
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 11,
          color: colors.textMuted,
          minWidth: 42,
          paddingTop: 2,
        }}
      >
        {time}
      </div>

      {/* Tag Chip */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          padding: "4px 10px",
          background: `${config.color}20`,
          borderRadius: 20,
          border: `1px solid ${config.color}40`,
        }}
      >
        <span style={{ fontSize: 14 }}>{config.emoji}</span>
        <span
          style={{
            fontSize: 11,
            fontWeight: 500,
            color: config.color,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          {config.label}
        </span>
      </div>

      {/* Description */}
      <div style={{ flex: 1, paddingTop: 4 }}>
        <div
          style={{
            fontSize: 13,
            color: colors.textPrimary,
            lineHeight: 1.4,
          }}
        >
          {event.description}
        </div>

        {/* Energy & Mood badges */}
        {(event.energy !== null || event.mood) && (
          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
            {event.energy !== null && (
              <span
                style={{
                  fontSize: 10,
                  padding: "2px 6px",
                  background: `${colors.neuralMint}20`,
                  color: colors.neuralMint,
                  borderRadius: 4,
                }}
              >
                ⚡ {event.energy}%
              </span>
            )}
            {event.mood && (
              <span
                style={{
                  fontSize: 10,
                  padding: "2px 6px",
                  background: `${colors.auroraLavender}20`,
                  color: colors.auroraLavender,
                  borderRadius: 4,
                }}
              >
                {event.mood}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Aurora Summary Card
// ═══════════════════════════════════════════════════════════════════

function SummaryCard() {
  const { data, loading, error } = useDaySummary();

  if (loading) {
    return (
      <div
        style={{
          padding: 20,
          background: gradients.cardSurface,
          borderRadius: 16,
          border: `1px solid ${colors.borderSubtle}`,
          marginBottom: 20,
        }}
      >
        <div style={{ color: colors.textMuted, fontSize: 13 }}>
          🧠 Aurora bugünü okuyor...
        </div>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  return (
    <div
      style={{
        padding: 20,
        background: `linear-gradient(135deg, rgba(175, 163, 255, 0.08) 0%, rgba(173, 95, 255, 0.05) 100%)`,
        borderRadius: 16,
        border: `1px solid ${colors.borderActive}`,
        marginBottom: 20,
        boxShadow: shadows.glow,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 14,
        }}
      >
        <span style={{ fontSize: 18 }}>✨</span>
        <span
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 13,
            fontWeight: 600,
            color: colors.auroraLavender,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}
        >
          Aurora's Read
        </span>
      </div>

      {/* Vibe Summary */}
      <div
        style={{
          fontSize: 16,
          fontWeight: 500,
          color: colors.textPrimary,
          marginBottom: 12,
          lineHeight: 1.5,
        }}
      >
        {data.vibe_summary}
      </div>

      {/* What Happened */}
      <div
        style={{
          fontSize: 13,
          color: colors.textSecondary,
          lineHeight: 1.6,
          marginBottom: 16,
          paddingLeft: 12,
          borderLeft: `2px solid ${colors.borderLight}`,
        }}
      >
        {data.what_happened}
      </div>

      {/* Evening & Energy */}
      <div style={{ display: "flex", gap: 12 }}>
        <div
          style={{
            flex: 1,
            padding: "10px 12px",
            background: "rgba(0, 245, 160, 0.08)",
            borderRadius: 10,
            border: `1px solid rgba(0, 245, 160, 0.2)`,
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: colors.neuralMint,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 4,
            }}
          >
            🌙 Akşam için
          </div>
          <div style={{ fontSize: 12, color: colors.textPrimary }}>
            {data.evening_suggestion}
          </div>
        </div>

        <div
          style={{
            flex: 1,
            padding: "10px 12px",
            background: "rgba(175, 163, 255, 0.08)",
            borderRadius: 10,
            border: `1px solid rgba(175, 163, 255, 0.2)`,
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: colors.auroraLavender,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 4,
            }}
          >
            ⚡ Enerji
          </div>
          <div style={{ fontSize: 12, color: colors.textPrimary }}>
            {data.energy_advice}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quick Log Form
// ═══════════════════════════════════════════════════════════════════

function QuickLogForm({ onLogged }: { onLogged: () => void }) {
  const [tag, setTag] = useState("");
  const [desc, setDesc] = useState("");
  const [loading, setLoading] = useState(false);

  const quickTags = ["walk", "coffee", "work", "sugoda", "gym", "low_energy"];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tag || !desc) return;

    setLoading(true);
    try {
      await logEvent(tag, desc);
      setTag("");
      setDesc("");
      onLogged();
    } catch (err) {
      console.error("Log error:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
      {/* Quick Tags */}
      <div style={{ display: "flex", gap: 6, marginBottom: 10, flexWrap: "wrap" }}>
        {quickTags.map((t) => {
          const config = getTagConfig(t);
          const isActive = tag === t;
          return (
            <button
              key={t}
              type="button"
              onClick={() => setTag(t)}
              style={{
                padding: "6px 12px",
                background: isActive ? `${config.color}30` : "rgba(255,255,255,0.05)",
                border: `1px solid ${isActive ? config.color : colors.borderSubtle}`,
                borderRadius: 20,
                color: isActive ? config.color : colors.textSecondary,
                fontSize: 12,
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              {config.emoji} {config.label}
            </button>
          );
        })}
      </div>

      {/* Description Input */}
      <div style={{ display: "flex", gap: 10 }}>
        <input
          type="text"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="Ne yaptın?"
          style={{
            flex: 1,
            padding: "10px 14px",
            background: "rgba(255,255,255,0.05)",
            border: `1px solid ${colors.borderSubtle}`,
            borderRadius: 10,
            color: colors.textPrimary,
            fontSize: 13,
            outline: "none",
          }}
        />
        <button
          type="submit"
          disabled={!tag || !desc || loading}
          style={{
            padding: "10px 20px",
            background: loading
              ? colors.charcoal
              : gradients.lavenderGlow,
            border: "none",
            borderRadius: 10,
            color: colors.textPrimary,
            fontSize: 13,
            fontWeight: 500,
            cursor: loading ? "wait" : "pointer",
            opacity: !tag || !desc ? 0.5 : 1,
          }}
        >
          {loading ? "..." : "Log"}
        </button>
      </div>
    </form>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Timeline Tab
// ═══════════════════════════════════════════════════════════════════

export function TimelineTab() {
  const { data, loading, refetch } = useTimeline();
  const today = new Date().toLocaleDateString("tr-TR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <div style={{ padding: "16px 20px" }}>
      {/* Date Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 11,
              color: colors.textMuted,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 4,
            }}
          >
            📅 Story Mode
          </div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 500,
              color: colors.textPrimary,
              fontFamily: "'Space Grotesk', sans-serif",
            }}
          >
            {today}
          </div>
        </div>

        {data && (
          <div
            style={{
              padding: "6px 12px",
              background: "rgba(0, 245, 160, 0.1)",
              borderRadius: 20,
              border: `1px solid rgba(0, 245, 160, 0.3)`,
            }}
          >
            <span style={{ fontSize: 12, color: colors.neuralMint }}>
              {data.events.length} event
            </span>
          </div>
        )}
      </div>

      {/* Quick Log Form */}
      <QuickLogForm onLogged={refetch} />

      {/* Aurora Summary */}
      <SummaryCard />

      {/* Events List */}
      <div>
        {loading ? (
          <div style={{ color: colors.textMuted, fontSize: 13, textAlign: "center", padding: 40 }}>
            Yükleniyor...
          </div>
        ) : data?.events.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              padding: 40,
              color: colors.textMuted,
              fontSize: 13,
            }}
          >
            <div style={{ fontSize: 32, marginBottom: 12 }}>📝</div>
            <div>Bugün henüz event yok.</div>
            <div style={{ marginTop: 4, fontSize: 12 }}>
              Yukarıdan hızlıca log ekleyebilirsin.
            </div>
          </div>
        ) : (
          data?.events.map((event) => <EventCard key={event.id} event={event} />)
        )}
      </div>
    </div>
  );
}

