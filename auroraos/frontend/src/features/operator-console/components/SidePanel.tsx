/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   Operator Console — Side Panel (Right Column)                   ║
 * ║   User context, mode controls, quick actions                     ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React from "react";
import type { ConversationDetail, ConversationMode } from "../types";

interface Props {
  detail: ConversationDetail | null;
  onModeChange: (mode: ConversationMode) => void;
}

const MODE_CONFIG: Record<ConversationMode, { icon: string; label: string; desc: string }> = {
  AI_ONLY: {
    icon: "🤖",
    label: "AI Only",
    desc: "Tamamen otonom",
  },
  HYBRID_GHOST: {
    icon: "👻",
    label: "Hybrid",
    desc: "AI yazar, sen onaylarsın",
  },
  HUMAN_ONLY: {
    icon: "👤",
    label: "Human",
    desc: "Tamamen manuel",
  },
};

const VIP_TIERS: Record<string, { color: string; icon: string }> = {
  none: { color: "#6b7280", icon: "⚪" },
  silver: { color: "#9ca3af", icon: "🥈" },
  gold: { color: "#fbbf24", icon: "🥇" },
  platinum: { color: "#a78bfa", icon: "💎" },
};

export const SidePanel: React.FC<Props> = ({ detail, onModeChange }) => {
  if (!detail) {
    return (
      <div
        style={{
          width: 280,
          borderLeft: "1px solid #1f2937",
          background: "rgba(0,0,0,0.9)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#6b7280",
          fontSize: 12,
        }}
      >
        Context yok
      </div>
    );
  }

  return (
    <div
      style={{
        width: 280,
        borderLeft: "1px solid #1f2937",
        background: "rgba(0,0,0,0.9)",
        display: "flex",
        flexDirection: "column",
        overflowY: "auto",
      }}
    >
      {/* Mode Control */}
      <div
        style={{
          padding: 16,
          borderBottom: "1px solid #1f2937",
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "#9ca3af",
            marginBottom: 10,
            textTransform: "uppercase",
            letterSpacing: 1,
          }}
        >
          Konuşma Modu
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {(Object.keys(MODE_CONFIG) as ConversationMode[]).map((mode) => {
            const cfg = MODE_CONFIG[mode];
            const isActive = detail.mode === mode;
            
            return (
              <button
                key={mode}
                onClick={() => onModeChange(mode)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "10px 12px",
                  background: isActive ? "#4f46e5" : "#1f2937",
                  border: isActive ? "1px solid #6366f1" : "1px solid transparent",
                  borderRadius: 8,
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <span style={{ fontSize: 18 }}>{cfg.icon}</span>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 500, color: "#f3f4f6" }}>
                    {cfg.label}
                  </div>
                  <div style={{ fontSize: 10, color: "#9ca3af" }}>
                    {cfg.desc}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* User Info */}
      <div
        style={{
          padding: 16,
          borderBottom: "1px solid #1f2937",
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "#9ca3af",
            marginBottom: 10,
            textTransform: "uppercase",
            letterSpacing: 1,
          }}
        >
          Kullanıcı Bilgisi
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>External ID</span>
            <span style={{ fontSize: 11, color: "#e5e7eb", fontFamily: "monospace" }}>
              {detail.external_user_id}
            </span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>Origin</span>
            <span style={{ fontSize: 11, color: "#e5e7eb" }}>
              {detail.origin}
            </span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>Coins Spent</span>
            <span style={{ fontSize: 11, color: "#fbbf24" }}>
              🪙 {detail.coins_spent}
            </span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>Mesaj Sayısı</span>
            <span style={{ fontSize: 11, color: "#e5e7eb" }}>
              {detail.message_count}
            </span>
          </div>
        </div>
      </div>

      {/* Performer Info */}
      <div
        style={{
          padding: 16,
          borderBottom: "1px solid #1f2937",
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "#9ca3af",
            marginBottom: 10,
            textTransform: "uppercase",
            letterSpacing: 1,
          }}
        >
          Performer
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>Slot</span>
            <span style={{ fontSize: 11, color: "#e5e7eb" }}>
              {detail.performer_slot_label}
            </span>
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontSize: 11, color: "#6b7280" }}>Agent ID</span>
            <span style={{ fontSize: 11, color: "#e5e7eb", fontFamily: "monospace" }}>
              {detail.agent_id}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div
        style={{
          padding: 16,
        }}
      >
        <div
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "#9ca3af",
            marginBottom: 10,
            textTransform: "uppercase",
            letterSpacing: 1,
          }}
        >
          Hızlı Eylemler
        </div>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <button
            style={{
              padding: "10px 12px",
              background: "#1f2937",
              border: "none",
              borderRadius: 8,
              color: "#e5e7eb",
              fontSize: 12,
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            📋 Konuşmayı Kopyala
          </button>
          
          <button
            style={{
              padding: "10px 12px",
              background: "#1f2937",
              border: "none",
              borderRadius: 8,
              color: "#e5e7eb",
              fontSize: 12,
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            🏷️ VIP Yap
          </button>
          
          <button
            style={{
              padding: "10px 12px",
              background: "#7f1d1d",
              border: "none",
              borderRadius: 8,
              color: "#fecaca",
              fontSize: 12,
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            🚫 Konuşmayı Kapat
          </button>
        </div>
      </div>

      {/* Status */}
      <div
        style={{
          marginTop: "auto",
          padding: 16,
          borderTop: "1px solid #1f2937",
          background: "rgba(0,0,0,0.5)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 10,
            color: "#6b7280",
          }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: detail.is_active ? "#10b981" : "#ef4444",
            }}
          />
          {detail.is_active ? "Aktif" : "Kapandı"}
          <span style={{ marginLeft: "auto" }}>
            {detail.priority}
          </span>
        </div>
      </div>
    </div>
  );
};

