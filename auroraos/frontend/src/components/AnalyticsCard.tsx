/**
 * AuroraOS — Analytics Dashboard Card
 * "Her decisions shape the intelligence."
 * 
 * Shows Betül's decision patterns and strong feedback signals.
 */

import { useEffect, useState } from "react";
import { fetchAnalytics, fetchVibePerformance } from "../api";
import type { AnalyticsSummary, VibePerformance } from "../api";
import { colors } from "../brand/colors";

export function AnalyticsCard() {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [vibeData, setVibeData] = useState<VibePerformance | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [summary, vibe] = await Promise.all([
          fetchAnalytics(),
          fetchVibePerformance(),
        ]);
        setData(summary);
        setVibeData(vibe);
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : "Error";
        setError(message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          padding: 16,
          margin: 16,
          borderRadius: 16,
          border: `1px solid ${colors.borderSubtle}`,
          background: "rgba(0,0,0,0.3)",
        }}
      >
        <div style={{ fontSize: 12, opacity: 0.5, textAlign: "center" }}>
          Analytics yükleniyor…
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div
        style={{
          padding: 16,
          margin: 16,
          borderRadius: 16,
          border: `1px solid ${colors.borderSubtle}`,
          background: "rgba(0,0,0,0.3)",
        }}
      >
        <div style={{ fontSize: 12, opacity: 0.5, textAlign: "center" }}>
          Analytics yüklenemedi
        </div>
      </div>
    );
  }

  const strongPos = data.strong_feedback.find(
    (x) => x.feedback_type === "strong_positive"
  )?.count ?? 0;
  const strongNeg = data.strong_feedback.find(
    (x) => x.feedback_type === "strong_negative"
  )?.count ?? 0;
  
  const approveCount = data.decision_counts.find(
    (x) => x.decision === "approve"
  )?.count ?? 0;
  const rejectCount = data.decision_counts.find(
    (x) => x.decision === "reject"
  )?.count ?? 0;

  const totalDecisions = approveCount + rejectCount;
  const approvalRate = totalDecisions > 0 
    ? Math.round((approveCount / totalDecisions) * 100) 
    : 0;

  return (
    <div
      style={{
        padding: 20,
        margin: 16,
        borderRadius: 16,
        border: `1px solid ${colors.borderSubtle}`,
        background: "rgba(0,0,0,0.4)",
        backdropFilter: "blur(10px)",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <div
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 14,
            fontWeight: 500,
            color: colors.textPrimary,
          }}
        >
          Aurora Snapshot
        </div>
        <div
          style={{
            fontSize: 10,
            opacity: 0.4,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}
        >
          Analytics
        </div>
      </div>

      {/* Strong Feedback Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          marginBottom: 16,
        }}
      >
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            background: "rgba(0, 245, 160, 0.1)",
            border: "1px solid rgba(0, 245, 160, 0.2)",
          }}
        >
          <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 4 }}>
            ⭐ Bu çok ben
          </div>
          <div
            style={{
              fontSize: 24,
              fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
              color: colors.neuralMint,
            }}
          >
            {strongPos}
          </div>
        </div>
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.2)",
          }}
        >
          <div style={{ fontSize: 11, opacity: 0.7, marginBottom: 4 }}>
            🚫 Asla ben değil
          </div>
          <div
            style={{
              fontSize: 24,
              fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
              color: "#f87171",
            }}
          >
            {strongNeg}
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 12,
          marginBottom: 16,
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 10, opacity: 0.5, marginBottom: 4 }}>
            Toplam Karar
          </div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {data.total_decisions}
          </div>
        </div>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 10, opacity: 0.5, marginBottom: 4 }}>
            Onay Oranı
          </div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
              color: colors.neuralMint,
            }}
          >
            {approvalRate}%
          </div>
        </div>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 10, opacity: 0.5, marginBottom: 4 }}>
            İçerik
          </div>
          <div
            style={{
              fontSize: 18,
              fontWeight: 600,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            {data.total_content}
          </div>
        </div>
      </div>

      {/* Best Vibe */}
      {vibeData?.best_vibe && (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            background: "rgba(175, 163, 255, 0.1)",
            border: `1px solid rgba(175, 163, 255, 0.2)`,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 10, opacity: 0.6, marginBottom: 4 }}>
            En Sevilen Vibe
          </div>
          <div
            style={{
              fontSize: 14,
              fontWeight: 500,
              color: colors.auroraLavender,
            }}
          >
            {vibeData.best_vibe === "soft_femme" && "🌸 Soft Femme"}
            {vibeData.best_vibe === "sweet_sarcasm_plus" && "😏 Sweet Sarcasm+"}
            {vibeData.best_vibe === "femme_fatale_hd" && "🖤 Femme Fatale"}
          </div>
        </div>
      )}

      {/* Vibe Performance Bars */}
      {vibeData && Object.keys(vibeData.vibe_performance).length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div
            style={{
              fontSize: 10,
              opacity: 0.5,
              marginBottom: 8,
              textTransform: "uppercase",
              letterSpacing: "0.1em",
            }}
          >
            Vibe Performansı
          </div>
          {Object.entries(vibeData.vibe_performance).map(([vibe, stats]) => (
            <div key={vibe} style={{ marginBottom: 8 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 11,
                  marginBottom: 4,
                }}
              >
                <span style={{ opacity: 0.7 }}>
                  {vibe === "soft_femme" && "🌸"}
                  {vibe === "sweet_sarcasm_plus" && "😏"}
                  {vibe === "femme_fatale_hd" && "🖤"}{" "}
                  {vibe.replace(/_/g, " ")}
                </span>
                <span style={{ opacity: 0.5 }}>
                  {stats.total > 0 ? `${stats.approval_rate}%` : "-"}
                </span>
              </div>
              <div
                style={{
                  height: 4,
                  background: "rgba(255,255,255,0.1)",
                  borderRadius: 999,
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${stats.approval_rate}%`,
                    background: `linear-gradient(90deg, ${colors.auroraLavender}, ${colors.femmeViolet})`,
                    borderRadius: 999,
                    transition: "width 0.5s ease",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

