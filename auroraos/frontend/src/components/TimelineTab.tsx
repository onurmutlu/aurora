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
  const { data, loading, error, refetch } = useDaySummary();

  if (loading) {
    return (
      <div
        style={{
          padding: 20,
          background: `linear-gradient(135deg, rgba(175, 163, 255, 0.05) 0%, rgba(173, 95, 255, 0.03) 100%)`,
          borderRadius: 16,
          border: `1px solid ${colors.borderSubtle}`,
          marginBottom: 20,
        }}
      >
        <div 
          style={{ 
            color: colors.auroraLavender, 
            fontSize: 13, 
            display: "flex", 
            alignItems: "center", 
            gap: 10 
          }}
        >
          <span className="animate-pulse" style={{ fontSize: 20 }}>🧠</span>
          <span>Aurora seni okuyor...</span>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div
        style={{
          padding: 16,
          background: "rgba(255, 100, 100, 0.05)",
          borderRadius: 12,
          border: `1px solid rgba(255, 100, 100, 0.2)`,
          marginBottom: 20,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <span style={{ color: colors.textMuted, fontSize: 12 }}>
          Aurora bağlanamadı
        </span>
        <button
          onClick={() => refetch()}
          style={{
            padding: "4px 10px",
            background: "rgba(175, 163, 255, 0.2)",
            border: "none",
            borderRadius: 8,
            color: colors.auroraLavender,
            fontSize: 11,
            cursor: "pointer",
          }}
        >
          Tekrar dene
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 16,
        background: `linear-gradient(135deg, rgba(175, 163, 255, 0.1) 0%, rgba(173, 95, 255, 0.06) 100%)`,
        borderRadius: 16,
        border: `1px solid ${colors.borderActive}`,
        marginBottom: 20,
        boxShadow: shadows.glow,
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Decorative gradient orb */}
      <div
        style={{
          position: "absolute",
          top: -30,
          right: -30,
          width: 100,
          height: 100,
          background: `radial-gradient(circle, ${colors.auroraLavender}20, transparent)`,
          borderRadius: "50%",
          pointerEvents: "none",
        }}
      />

      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 16 }}>✨</span>
          <span
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: 11,
              fontWeight: 600,
              color: colors.auroraLavender,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
            }}
          >
            Aurora's Read
          </span>
        </div>
        <span
          style={{
            fontSize: 9,
            color: colors.textMuted,
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          AI-powered
        </span>
      </div>

      {/* Vibe Summary - Hero text */}
      <div
        style={{
          fontSize: 15,
          fontWeight: 500,
          color: colors.textPrimary,
          marginBottom: 14,
          lineHeight: 1.55,
          fontFamily: "'Inter', sans-serif",
        }}
      >
        {data.vibe_summary}
      </div>

      {/* What Happened - Story block */}
      <div
        style={{
          fontSize: 12,
          color: colors.textSecondary,
          lineHeight: 1.65,
          marginBottom: 14,
          padding: "10px 12px",
          background: "rgba(0, 0, 0, 0.2)",
          borderRadius: 10,
          borderLeft: `3px solid ${colors.auroraLavender}40`,
        }}
      >
        {data.what_happened}
      </div>

      {/* Evening & Energy - Compact cards */}
      <div style={{ display: "flex", gap: 8 }}>
        <div
          style={{
            flex: 1,
            padding: "10px",
            background: "rgba(0, 245, 160, 0.06)",
            borderRadius: 10,
            border: `1px solid rgba(0, 245, 160, 0.15)`,
          }}
        >
          <div
            style={{
              fontSize: 9,
              color: colors.neuralMint,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 5,
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            <span>🌙</span> Akşam İçin
          </div>
          <div style={{ fontSize: 11, color: colors.textPrimary, lineHeight: 1.5 }}>
            {data.evening_suggestion}
          </div>
        </div>

        <div
          style={{
            flex: 1,
            padding: "10px",
            background: "rgba(175, 163, 255, 0.06)",
            borderRadius: 10,
            border: `1px solid rgba(175, 163, 255, 0.15)`,
          }}
        >
          <div
            style={{
              fontSize: 9,
              color: colors.auroraLavender,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 5,
              display: "flex",
              alignItems: "center",
              gap: 4,
            }}
          >
            <span>⚡</span> Enerji Tavsiyesi
          </div>
          <div style={{ fontSize: 11, color: colors.textPrimary, lineHeight: 1.5 }}>
            {data.energy_advice}
          </div>
        </div>
      </div>

      {/* Refresh hint */}
      <div
        style={{
          marginTop: 12,
          textAlign: "center",
        }}
      >
        <button
          onClick={() => refetch()}
          style={{
            padding: "4px 12px",
            background: "transparent",
            border: `1px solid ${colors.borderSubtle}`,
            borderRadius: 20,
            color: colors.textMuted,
            fontSize: 10,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
        >
          🔄 Yeniden oku
        </button>
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

