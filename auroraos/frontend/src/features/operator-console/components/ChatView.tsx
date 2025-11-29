/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   Operator Console — Chat View (Center Column)                   ║
 * ║   Message thread + reply input                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useRef, useEffect } from "react";
import type { ConversationDetail, ConversationMessage } from "../types";

interface Props {
  detail: ConversationDetail | null;
  loading: boolean;
  onSend: (text: string, sendAs: "operator" | "agent_style") => Promise<void>;
  onRefresh: () => void;
}

const SENDER_STYLES: Record<string, { bg: string; label: string; align: string }> = {
  user: { bg: "#1f2937", label: "Kullanıcı", align: "left" },
  agent: { bg: "#4338ca", label: "AI Agent", align: "right" },
  operator: { bg: "#059669", label: "Operator", align: "right" },
};

export const ChatView: React.FC<Props> = ({ detail, loading, onSend, onRefresh }) => {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sendAs, setSendAs] = useState<"operator" | "agent_style">("agent_style");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [detail?.messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;
    
    setSending(true);
    try {
      await onSend(text, sendAs);
      setInput("");
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString("tr-TR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Empty state
  if (!detail) {
    return (
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(0,0,0,0.8)",
          color: "#6b7280",
        }}
      >
        <span style={{ fontSize: 48, marginBottom: 16 }}>💬</span>
        <span style={{ fontSize: 14 }}>Bir konuşma seç</span>
      </div>
    );
  }

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        background: "rgba(0,0,0,0.8)",
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
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#f3f4f6" }}>
            Konuşma #{detail.id}
          </div>
          <div style={{ fontSize: 11, color: "#9ca3af" }}>
            {detail.performer_slot_label} · {detail.mode} · {detail.origin.toLowerCase()}
          </div>
        </div>
        <button
          onClick={onRefresh}
          style={{
            background: "#374151",
            color: "#e5e7eb",
            border: "none",
            borderRadius: 6,
            padding: "6px 12px",
            fontSize: 11,
            cursor: "pointer",
          }}
        >
          🔄 Yenile
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {loading && (
          <div style={{ textAlign: "center", color: "#6b7280", fontSize: 12 }}>
            Yükleniyor...
          </div>
        )}
        
        {detail.messages.map((m) => {
          const style = SENDER_STYLES[m.sender] || SENDER_STYLES.user;
          const isUser = m.sender === "user";
          
          return (
            <div
              key={m.id}
              style={{
                display: "flex",
                justifyContent: isUser ? "flex-start" : "flex-end",
              }}
            >
              <div
                style={{
                  maxWidth: "70%",
                  background: style.bg,
                  borderRadius: 12,
                  padding: "10px 14px",
                }}
              >
                {/* Sender label */}
                {!isUser && (
                  <div
                    style={{
                      fontSize: 10,
                      opacity: 0.7,
                      marginBottom: 4,
                      color: "#e5e7eb",
                    }}
                  >
                    {style.label}
                    {m.is_draft && " (Taslak)"}
                    {m.edited_by_operator && " ✏️"}
                  </div>
                )}
                
                {/* Message text */}
                <div
                  style={{
                    fontSize: 13,
                    color: "#f3f4f6",
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {m.text}
                </div>
                
                {/* Timestamp */}
                <div
                  style={{
                    fontSize: 9,
                    opacity: 0.5,
                    marginTop: 6,
                    color: "#e5e7eb",
                    textAlign: isUser ? "left" : "right",
                  }}
                >
                  {formatTime(m.created_at)}
                </div>
              </div>
            </div>
          );
        })}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div
        style={{
          borderTop: "1px solid #1f2937",
          padding: 12,
          background: "rgba(0,0,0,0.5)",
        }}
      >
        {/* Send As toggle */}
        <div
          style={{
            display: "flex",
            gap: 8,
            marginBottom: 8,
          }}
        >
          <span style={{ fontSize: 11, color: "#9ca3af" }}>Gönder:</span>
          <button
            onClick={() => setSendAs("agent_style")}
            style={{
              background: sendAs === "agent_style" ? "#4338ca" : "#374151",
              color: "#e5e7eb",
              border: "none",
              borderRadius: 4,
              padding: "3px 8px",
              fontSize: 10,
              cursor: "pointer",
            }}
          >
            🤖 Agent Stili
          </button>
          <button
            onClick={() => setSendAs("operator")}
            style={{
              background: sendAs === "operator" ? "#059669" : "#374151",
              color: "#e5e7eb",
              border: "none",
              borderRadius: 4,
              padding: "3px 8px",
              fontSize: 10,
              cursor: "pointer",
            }}
          >
            👤 Operator
          </button>
        </div>

        {/* Text input + Send button */}
        <div style={{ display: "flex", gap: 8 }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Mesaj yaz... (Enter gönderir, Shift+Enter satır atlar)"
            style={{
              flex: 1,
              background: "#1f2937",
              color: "#f3f4f6",
              border: "none",
              borderRadius: 8,
              padding: "10px 14px",
              fontSize: 13,
              resize: "none",
              height: 60,
              outline: "none",
            }}
          />
          <button
            onClick={handleSend}
            disabled={sending || !input.trim()}
            style={{
              width: 80,
              background: sending ? "#4b5563" : "#4f46e5",
              color: "white",
              border: "none",
              borderRadius: 8,
              fontSize: 13,
              fontWeight: 500,
              cursor: sending ? "not-allowed" : "pointer",
              opacity: !input.trim() ? 0.5 : 1,
            }}
          >
            {sending ? "..." : "Gönder"}
          </button>
        </div>
      </div>
    </div>
  );
};

