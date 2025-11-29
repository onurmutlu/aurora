/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Operator Console — Main Component                     ║
 * ║   Betül's Cockpit for managing AI conversations                  ║
 * ║                                                                  ║
 * ║   3-Column Layout:                                               ║
 * ║   [Conversations] [Chat View] [Context Panel]                    ║
 * ║                                                                  ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React, { useEffect, useState, useCallback } from "react";
import {
  fetchConversations,
  fetchConversationDetail,
  sendOperatorReply,
  updateConversationMode,
} from "./api";
import type {
  ConversationSummary,
  ConversationDetail,
  ConversationMode,
} from "./types";
import { ConversationList } from "./components/ConversationList";
import { ChatView } from "./components/ChatView";
import { SidePanel } from "./components/SidePanel";

const POLL_INTERVAL = 5000; // 5 seconds

export const OperatorConsole: React.FC = () => {
  // State
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<ConversationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [modeFilter, setModeFilter] = useState<ConversationMode | "ALL">("ALL");
  const [isOnline, setIsOnline] = useState(true);

  // Fetch conversations list
  const loadConversations = useCallback(async () => {
    try {
      const list = await fetchConversations({
        mode: modeFilter === "ALL" ? undefined : modeFilter,
        active_only: true,
      });
      setConversations(list);
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
    } finally {
      setLoading(false);
    }
  }, [modeFilter]);

  // Fetch single conversation detail
  const loadDetail = useCallback(async (id: number) => {
    setLoadingDetail(true);
    try {
      const detail = await fetchConversationDetail(id);
      setSelectedDetail(detail);
    } catch (err) {
      console.error("Failed to fetch conversation detail:", err);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  // Initial load + polling
  useEffect(() => {
    loadConversations();
    const interval = setInterval(loadConversations, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [loadConversations]);

  // Auto-refresh detail when selected
  useEffect(() => {
    if (!selectedId) return;
    
    const interval = setInterval(() => {
      loadDetail(selectedId);
    }, POLL_INTERVAL);
    
    return () => clearInterval(interval);
  }, [selectedId, loadDetail]);

  // Handlers
  const handleSelectConversation = (id: number) => {
    setSelectedId(id);
    loadDetail(id);
  };

  const handleSend = async (text: string, sendAs: "operator" | "agent_style") => {
    if (!selectedId) return;
    
    try {
      await sendOperatorReply({
        conversationId: selectedId,
        text,
        sendAs,
      });
      // Refresh detail to show new message
      await loadDetail(selectedId);
    } catch (err) {
      console.error("Failed to send reply:", err);
      alert("Mesaj gönderilemedi!");
    }
  };

  const handleModeChange = async (mode: ConversationMode) => {
    if (!selectedId) return;
    
    try {
      await updateConversationMode(selectedId, mode);
      await loadDetail(selectedId);
      await loadConversations();
    } catch (err) {
      console.error("Failed to change mode:", err);
    }
  };

  const handleRefresh = () => {
    if (selectedId) {
      loadDetail(selectedId);
    }
    loadConversations();
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        background: "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)",
        color: "#f3f4f6",
        display: "flex",
        flexDirection: "column",
        fontFamily: "'Inter', -apple-system, sans-serif",
      }}
    >
      {/* Top Bar */}
      <header
        style={{
          height: 56,
          background: "rgba(0,0,0,0.8)",
          borderBottom: "1px solid #1f2937",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 20px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 24 }}>🎛️</span>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: "#f3f4f6" }}>
              AuroraOS Operator Console
            </div>
            <div style={{ fontSize: 10, color: "#6b7280" }}>
              Betül's Cockpit · v1.0
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {/* Stats */}
          <div
            style={{
              display: "flex",
              gap: 12,
              fontSize: 11,
              color: "#9ca3af",
            }}
          >
            <span>💬 {conversations.length} aktif</span>
            <span>
              🟣 {conversations.filter((c) => c.priority === "VIP").length} VIP
            </span>
            <span>
              👻 {conversations.filter((c) => c.mode === "HYBRID_GHOST").length} hybrid
            </span>
          </div>

          {/* Online toggle */}
          <button
            onClick={() => setIsOnline(!isOnline)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "6px 12px",
              background: isOnline ? "#059669" : "#4b5563",
              border: "none",
              borderRadius: 20,
              color: "white",
              fontSize: 11,
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: isOnline ? "#a7f3d0" : "#9ca3af",
              }}
            />
            {isOnline ? "Çevrimiçi" : "Çevrimdışı"}
          </button>
        </div>
      </header>

      {/* Main Content - 3 Column Layout */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left: Conversation List */}
        <div style={{ width: 320 }}>
          <ConversationList
            conversations={conversations}
            selectedId={selectedId}
            onSelect={handleSelectConversation}
            modeFilter={modeFilter}
            onModeFilterChange={setModeFilter}
            loading={loading}
          />
        </div>

        {/* Center: Chat View */}
        <ChatView
          detail={selectedDetail}
          loading={loadingDetail}
          onSend={handleSend}
          onRefresh={handleRefresh}
        />

        {/* Right: Context Panel */}
        <SidePanel
          detail={selectedDetail}
          onModeChange={handleModeChange}
        />
      </div>
    </div>
  );
};

export default OperatorConsole;

