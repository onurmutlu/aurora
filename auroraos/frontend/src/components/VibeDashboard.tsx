/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS — Vibe Dashboard / Stats Tab                          ║
 * ║   Sprint 007: Visual Dashboard                                   ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import { useState } from "react";
import { colors, gradients, shadows } from "../brand/colors";
import { useDayStats, useAnalytics, useDaySummary, useContentWall } from "../hooks/useAuroraAPI";

// ═══════════════════════════════════════════════════════════════════
// Stat Card Component
// ═══════════════════════════════════════════════════════════════════

interface StatCardProps {
  label: string;
  value: string | number;
  icon: string;
  color: string;
  subtext?: string;
}

function StatCard({ label, value, icon, color, subtext }: StatCardProps) {
  return (
    <div
      style={{
        flex: 1,
        padding: "16px 14px",
        background: gradients.cardSurface,
        borderRadius: 14,
        border: `1px solid ${colors.borderSubtle}`,
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: 24, marginBottom: 6 }}>{icon}</div>
      <div
        style={{
          fontSize: 28,
          fontWeight: 600,
          color: color,
          fontFamily: "'Space Grotesk', sans-serif",
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: 10,
          color: colors.textMuted,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginTop: 4,
        }}
      >
        {label}
      </div>
      {subtext && (
        <div style={{ fontSize: 11, color: colors.textSecondary, marginTop: 4 }}>
          {subtext}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tag Heatmap
// ═══════════════════════════════════════════════════════════════════

function TagHeatmap() {
  const { data, loading } = useDayStats();

  if (loading || !data) {
    return null;
  }

  const maxCount = Math.max(...data.top_tags.map((t) => t.count), 1);

  const tagEmojis: Record<string, string> = {
    walk: "🚶",
    gym: "💪",
    starbucks: "☕",
    coffee: "☕",
    sugoda: "🎙",
    work: "💼",
    dm: "💬",
    low_energy: "🪫",
    happy: "😊",
    tired: "😴",
  };

  return (
    <div
      style={{
        padding: 16,
        background: gradients.cardSurface,
        borderRadius: 14,
        border: `1px solid ${colors.borderSubtle}`,
        marginBottom: 16,
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: colors.textMuted,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: 14,
        }}
      >
        🏷️ Top Tags
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {data.top_tags.map((tag) => {
          const percent = (tag.count / maxCount) * 100;
          const emoji = tagEmojis[tag.tag.toLowerCase()] || "•";

          return (
            <div key={tag.tag}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 4,
                }}
              >
                <span style={{ fontSize: 12, color: colors.textPrimary }}>
                  {emoji} {tag.tag}
                </span>
                <span style={{ fontSize: 11, color: colors.textMuted }}>
                  {tag.count}x
                </span>
              </div>
              <div
                style={{
                  height: 6,
                  background: "rgba(255,255,255,0.05)",
                  borderRadius: 3,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${percent}%`,
                    background: gradients.lavenderGlow,
                    borderRadius: 3,
                    transition: "width 0.5s ease",
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Feedback Stats
// ═══════════════════════════════════════════════════════════════════

function FeedbackStats() {
  const { data, loading } = useAnalytics();

  if (loading || !data) {
    return null;
  }

  const strongPos =
    data.strong_feedback.find((f) => f.feedback_type === "strong_positive")?.count || 0;
  const strongNeg =
    data.strong_feedback.find((f) => f.feedback_type === "strong_negative")?.count || 0;

  return (
    <div
      style={{
        padding: 16,
        background: gradients.cardSurface,
        borderRadius: 14,
        border: `1px solid ${colors.borderSubtle}`,
        marginBottom: 16,
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: colors.textMuted,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: 14,
        }}
      >
        🎯 Betül Feedback
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <div
          style={{
            flex: 1,
            padding: "12px",
            background: "rgba(0, 245, 160, 0.08)",
            borderRadius: 10,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 24 }}>⭐</div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 600,
              color: colors.neuralMint,
              marginTop: 4,
            }}
          >
            {strongPos}
          </div>
          <div style={{ fontSize: 10, color: colors.textMuted, marginTop: 2 }}>
            Bu çok ben
          </div>
        </div>

        <div
          style={{
            flex: 1,
            padding: "12px",
            background: "rgba(255, 107, 107, 0.08)",
            borderRadius: 10,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 24 }}>🚫</div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 600,
              color: "#FF6B6B",
              marginTop: 4,
            }}
          >
            {strongNeg}
          </div>
          <div style={{ fontSize: 10, color: colors.textMuted, marginTop: 2 }}>
            Asla ben değil
          </div>
        </div>

        <div
          style={{
            flex: 1,
            padding: "12px",
            background: "rgba(175, 163, 255, 0.08)",
            borderRadius: 10,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 24 }}>📊</div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 600,
              color: colors.auroraLavender,
              marginTop: 4,
            }}
          >
            {data.total_decisions}
          </div>
          <div style={{ fontSize: 10, color: colors.textMuted, marginTop: 2 }}>
            Toplam karar
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Content Wall (Approved Content)
// ═══════════════════════════════════════════════════════════════════

function ContentWall() {
  const { data, loading } = useContentWall(10);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  const vibeEmojis: Record<string, string> = {
    soft_femme: "🌸",
    sweet_sarcasm_plus: "😏",
    femme_fatale_hd: "🖤",
  };

  const handleCopy = async (text: string, id: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          padding: 16,
          background: gradients.cardSurface,
          borderRadius: 14,
          border: `1px solid ${colors.borderSubtle}`,
          marginBottom: 16,
          textAlign: "center",
          color: colors.textMuted,
        }}
      >
        Yükleniyor...
      </div>
    );
  }

  if (!data || data.count === 0) {
    return (
      <div
        style={{
          padding: 20,
          background: gradients.cardSurface,
          borderRadius: 14,
          border: `1px solid ${colors.borderSubtle}`,
          marginBottom: 16,
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: 24, marginBottom: 8 }}>📝</div>
        <div style={{ fontSize: 13, color: colors.textMuted }}>
          Henüz onaylı içerik yok.
        </div>
        <div style={{ fontSize: 11, color: colors.textMuted, marginTop: 4 }}>
          İçerik oluştur ve onayla, burada görünsün.
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 16,
        background: gradients.cardSurface,
        borderRadius: 14,
        border: `1px solid ${colors.borderSubtle}`,
        marginBottom: 16,
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: colors.textMuted,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          marginBottom: 14,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>📋 Content Wall</span>
        <span style={{ color: colors.auroraLavender }}>{data.count} içerik</span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {data.items.slice(0, 5).map((item) => {
          const emoji = vibeEmojis[item.vibe_mode] || "✨";
          const isCopied = copiedId === item.id;

          return (
            <div
              key={item.id}
              style={{
                padding: "12px 14px",
                background: "rgba(0, 0, 0, 0.2)",
                borderRadius: 10,
                border: `1px solid ${isCopied ? colors.neuralMint : colors.borderSubtle}`,
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              onClick={() => handleCopy(item.text, item.id)}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: 6,
                }}
              >
                <span
                  style={{
                    fontSize: 10,
                    color: colors.textMuted,
                    background: "rgba(255,255,255,0.05)",
                    padding: "2px 6px",
                    borderRadius: 4,
                  }}
                >
                  {emoji} {item.vibe_mode}
                </span>
                <span
                  style={{
                    fontSize: 10,
                    color: isCopied ? colors.neuralMint : colors.textMuted,
                    fontWeight: isCopied ? 600 : 400,
                  }}
                >
                  {isCopied ? "✓ Kopyalandı!" : "Kopyala →"}
                </span>
              </div>
              <div
                style={{
                  fontSize: 13,
                  color: colors.textPrimary,
                  lineHeight: 1.5,
                }}
              >
                {item.text}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Aurora Advice Card
// ═══════════════════════════════════════════════════════════════════

function AuroraAdviceCard() {
  const { data, loading } = useDaySummary();

  if (loading || !data) {
    return null;
  }

  return (
    <div
      style={{
        padding: 20,
        background: `linear-gradient(135deg, rgba(175, 163, 255, 0.1) 0%, rgba(173, 95, 255, 0.05) 100%)`,
        borderRadius: 16,
        border: `1px solid ${colors.borderActive}`,
        boxShadow: shadows.glow,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 14,
        }}
      >
        <span style={{ fontSize: 18 }}>🧠</span>
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
          Aurora Tavsiyesi
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <div
          style={{
            padding: "12px 14px",
            background: "rgba(0, 0, 0, 0.3)",
            borderRadius: 10,
            borderLeft: `3px solid ${colors.neuralMint}`,
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: colors.neuralMint,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 6,
            }}
          >
            🌙 Akşam için
          </div>
          <div style={{ fontSize: 13, color: colors.textPrimary, lineHeight: 1.5 }}>
            {data.evening_suggestion}
          </div>
        </div>

        <div
          style={{
            padding: "12px 14px",
            background: "rgba(0, 0, 0, 0.3)",
            borderRadius: 10,
            borderLeft: `3px solid ${colors.auroraLavender}`,
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: colors.auroraLavender,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
              marginBottom: 6,
            }}
          >
            ⚡ Enerji
          </div>
          <div style={{ fontSize: 13, color: colors.textPrimary, lineHeight: 1.5 }}>
            {data.energy_advice}
          </div>
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main Vibe Dashboard
// ═══════════════════════════════════════════════════════════════════

export function VibeDashboard() {
  const { data: dayStats } = useDayStats();
  const { data: analytics } = useAnalytics();

  return (
    <div style={{ padding: "16px 20px" }}>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <div
          style={{
            fontSize: 11,
            color: colors.textMuted,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            marginBottom: 4,
          }}
        >
          📊 Vibe Dashboard
        </div>
        <div
          style={{
            fontSize: 18,
            fontWeight: 500,
            color: colors.textPrimary,
            fontFamily: "'Space Grotesk', sans-serif",
          }}
        >
          Aurora Analytics
        </div>
      </div>

      {/* Quick Stats */}
      <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
        <StatCard
          label="Gün"
          value={dayStats?.total_days || 0}
          icon="📅"
          color={colors.auroraLavender}
        />
        <StatCard
          label="Event"
          value={dayStats?.total_events || 0}
          icon="📝"
          color={colors.neuralMint}
        />
        <StatCard
          label="İçerik"
          value={analytics?.total_content || 0}
          icon="✨"
          color={colors.femmeViolet}
        />
      </div>

      {/* Tag Heatmap */}
      <TagHeatmap />

      {/* Content Wall */}
      <ContentWall />

      {/* Feedback Stats */}
      <FeedbackStats />

      {/* Aurora Advice */}
      <AuroraAdviceCard />
    </div>
  );
}

