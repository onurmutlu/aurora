/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   Operator Console — Conversation List (Left Column)            ║
 * ║   Active conversations with filters                              ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React from "react";
import type { ConversationSummary, ConversationMode, ConversationPriority } from "../types";

interface Props {
  conversations: ConversationSummary[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  modeFilter: ConversationMode | "ALL";
  onModeFilterChange: (mode: ConversationMode | "ALL") => void;
  loading?: boolean;
}

const PRIORITY_COLORS: Record<ConversationPriority, string> = {
  VIP: "bg-purple-600 text-white",
  HIGH: "bg-orange-600 text-white",
  NORMAL: "bg-gray-700 text-gray-300",
  LOW: "bg-gray-800 text-gray-400",
};

const MODE_ICONS: Record<ConversationMode, string> = {
  AI_ONLY: "🤖",
  HYBRID_GHOST: "👻",
  HUMAN_ONLY: "👤",
};

const ORIGIN_COLORS: Record<string, string> = {
  FLIRTMARKET: "text-pink-400",
  TELEGRAM: "text-blue-400",
  WEB: "text-green-400",
  ONLYVIPS: "text-yellow-400",
};

export const ConversationList: React.FC<Props> = ({
  conversations,
  selectedId,
  onSelect,
  modeFilter,
  onModeFilterChange,
  loading,
}) => {
  const formatTime = (iso: string | null) => {
    if (!iso) return "";
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    
    if (diff < 60000) return "şimdi";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}dk`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}s`;
    return d.toLocaleDateString("tr-TR");
  };

  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid #1f2937",
        background: "rgba(0,0,0,0.9)",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid #1f2937",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18 }}>💬</span>
          <span style={{ fontWeight: 600, fontSize: 14, color: "#f3f4f6" }}>
            Konuşmalar
          </span>
          <span
            style={{
              background: "#4f46e5",
              color: "white",
              fontSize: 10,
              padding: "2px 6px",
              borderRadius: 10,
            }}
          >
            {conversations.length}
          </span>
        </div>
        
        <select
          value={modeFilter}
          onChange={(e) => onModeFilterChange(e.target.value as ConversationMode | "ALL")}
          style={{
            background: "#1f2937",
            color: "#e5e7eb",
            fontSize: 11,
            padding: "4px 8px",
            borderRadius: 6,
            border: "none",
            cursor: "pointer",
          }}
        >
          <option value="ALL">🎯 Tümü</option>
          <option value="AI_ONLY">🤖 AI Only</option>
          <option value="HYBRID_GHOST">👻 Hybrid</option>
          <option value="HUMAN_ONLY">👤 Human</option>
        </select>
      </div>

      {/* Conversation List */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {loading ? (
          <div
            style={{
              padding: 20,
              textAlign: "center",
              color: "#6b7280",
              fontSize: 12,
            }}
          >
            Yükleniyor...
          </div>
        ) : conversations.length === 0 ? (
          <div
            style={{
              padding: 20,
              textAlign: "center",
              color: "#6b7280",
              fontSize: 12,
            }}
          >
            Aktif konuşma yok.
          </div>
        ) : (
          conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.id)}
              style={{
                width: "100%",
                textAlign: "left",
                padding: "12px 16px",
                borderBottom: "1px solid #111827",
                background: selectedId === c.id ? "#1f2937" : "transparent",
                cursor: "pointer",
                border: "none",
                transition: "background 0.15s",
              }}
              onMouseEnter={(e) => {
                if (selectedId !== c.id) {
                  e.currentTarget.style.background = "rgba(31, 41, 55, 0.5)";
                }
              }}
              onMouseLeave={(e) => {
                if (selectedId !== c.id) {
                  e.currentTarget.style.background = "transparent";
                }
              }}
            >
              {/* Top row: ID + Origin + Time */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: 6,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span style={{ fontSize: 11, color: "#9ca3af" }}>
                    #{c.id}
                  </span>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 500,
                    }}
                    className={ORIGIN_COLORS[c.origin] || "text-gray-400"}
                  >
                    {c.origin.toLowerCase()}
                  </span>
                </div>
                <span style={{ fontSize: 10, color: "#6b7280" }}>
                  {formatTime(c.last_message_at)}
                </span>
              </div>

              {/* Message preview */}
              <div
                style={{
                  fontSize: 12,
                  color: "#e5e7eb",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  marginBottom: 8,
                }}
              >
                {c.last_message_preview || "Mesaj yok"}
              </div>

              {/* Bottom row: Mode + Priority + Stats */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  flexWrap: "wrap",
                }}
              >
                <span style={{ fontSize: 12 }}>{MODE_ICONS[c.mode]}</span>
                <span
                  style={{
                    fontSize: 9,
                    padding: "2px 6px",
                    borderRadius: 10,
                  }}
                  className={PRIORITY_COLORS[c.priority]}
                >
                  {c.priority}
                </span>
                <span style={{ fontSize: 10, color: "#6b7280" }}>
                  {c.performer_slot_label}
                </span>
                {c.coins_spent > 0 && (
                  <span style={{ fontSize: 10, color: "#fbbf24" }}>
                    🪙 {c.coins_spent}
                  </span>
                )}
                <span style={{ fontSize: 10, color: "#6b7280" }}>
                  💬 {c.message_count}
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
};

