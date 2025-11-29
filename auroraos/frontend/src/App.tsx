/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS — Betül Console v0.2                                  ║
 * ║   "From the void, her light."                                    ║
 * ║                                                                  ║
 * ║   Sprint 007: Visual Dashboard + Story Mode                      ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import { useState, useRef } from "react";
import { SplashScreen } from "./components/SplashScreen";
import { PendingList } from "./components/PendingList";
import { VibeBar } from "./components/VibeBar";
import { AnalyticsCard } from "./components/AnalyticsCard";
import { TimelineTab } from "./components/TimelineTab";
import { VibeDashboard } from "./components/VibeDashboard";
import { OperatorConsole } from "./features/operator-console";
import { StateDashboard } from "./features/state-dashboard";
import { AuroraLogoMark } from "./brand/Logo";
import { colors, gradients } from "./brand/colors";
import { BRAND } from "./brand";
import { useEngineStatus, generateContent, QUICK_SCENARIOS } from "./hooks/useAuroraAPI";

// ═══════════════════════════════════════════════════════════════════
// Tab Types
// ═══════════════════════════════════════════════════════════════════

type TabId = "inbox" | "story" | "stats" | "operator" | "state";

interface Tab {
  id: TabId;
  label: string;
  icon: string;
}

const TABS: Tab[] = [
  { id: "inbox", label: "Inbox", icon: "📥" },
  { id: "story", label: "Story", icon: "📖" },
  { id: "stats", label: "Stats", icon: "📊" },
  { id: "operator", label: "Console", icon: "🎛️" },
  { id: "state", label: "State", icon: "🏛️" },
];

// ═══════════════════════════════════════════════════════════════════
// Tab Button Component
// ═══════════════════════════════════════════════════════════════════

function TabButton({
  tab,
  isActive,
  onClick,
}: {
  tab: Tab;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "8px 16px",
        background: isActive
          ? `linear-gradient(135deg, ${colors.auroraLavender}20, ${colors.femmeViolet}15)`
          : "transparent",
        border: `1px solid ${isActive ? colors.borderActive : "transparent"}`,
        borderRadius: 20,
        color: isActive ? colors.auroraLavender : colors.textMuted,
        fontSize: 12,
        fontWeight: isActive ? 600 : 400,
        cursor: "pointer",
        transition: "all 0.2s ease",
        display: "flex",
        alignItems: "center",
        gap: 6,
      }}
    >
      <span style={{ fontSize: 14 }}>{tab.icon}</span>
      <span>{tab.label}</span>
    </button>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Quick Generate Panel
// ═══════════════════════════════════════════════════════════════════

function QuickGeneratePanel({ onGenerate }: { onGenerate: () => void }) {
  const [generating, setGenerating] = useState<string | null>(null);

  const handleGenerate = async (scenario: string) => {
    setGenerating(scenario);
    try {
      await generateContent(scenario);
      onGenerate();
    } catch (e) {
      console.error("Generate failed:", e);
    } finally {
      setGenerating(null);
    }
  };

  return (
    <div
      style={{
        padding: "8px 12px",
        background: `linear-gradient(135deg, ${colors.auroraLavender}08, ${colors.femmeViolet}05)`,
        borderBottom: `1px solid ${colors.borderSubtle}`,
      }}
    >
      <div
        style={{
          fontSize: 9,
          color: colors.textMuted,
          marginBottom: 6,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        ⚡ Quick Generate
      </div>
      <div
        style={{
          display: "flex",
          gap: 5,
          flexWrap: "wrap",
        }}
      >
        {QUICK_SCENARIOS.map((s) => (
          <button
            key={s.id}
            onClick={() => handleGenerate(s.id)}
            disabled={generating !== null}
            style={{
              padding: "4px 8px",
              background: generating === s.id
                ? colors.auroraLavender
                : `${colors.onyxBlack}cc`,
              border: `1px solid ${colors.borderSubtle}`,
              borderRadius: 10,
              color: generating === s.id ? colors.void : colors.textPrimary,
              fontSize: 10,
              cursor: generating ? "wait" : "pointer",
              transition: "all 0.2s ease",
              opacity: generating && generating !== s.id ? 0.5 : 1,
            }}
          >
            {generating === s.id ? "⏳" : s.icon} {s.label.split(" ").slice(1).join(" ")}
          </button>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Inbox Tab (Original Content)
// ═══════════════════════════════════════════════════════════════════

function InboxTab() {
  const pendingListRef = useRef<{ refetch: () => void } | null>(null);

  const handleNewContent = () => {
    // Trigger refetch after short delay
    setTimeout(() => {
      window.location.reload(); // Simple refresh for now
    }, 500);
  };

  return (
    <>
      <VibeBar />
      <QuickGeneratePanel onGenerate={handleNewContent} />
      <main>
        <PendingList />
        <AnalyticsCard />
      </main>
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main App
// ═══════════════════════════════════════════════════════════════════

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>("inbox");
  const { data: engineStatus } = useEngineStatus();

  if (showSplash) {
    return <SplashScreen onComplete={() => setShowSplash(false)} duration={3500} />;
  }

  return (
    <div
      className="animate-fadeIn"
      style={{
        minHeight: "100vh",
        background: `linear-gradient(180deg, ${colors.onyxBlack} 0%, ${colors.void} 50%, ${colors.deepVoidGray} 100%)`,
        color: colors.textPrimary,
      }}
    >
      {/* Header */}
      <header
        style={{
          padding: "20px 20px 16px",
          background: "rgba(0,0,0,0.4)",
          borderBottom: `1px solid ${colors.borderSubtle}`,
          backdropFilter: "blur(10px)",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        {/* Top Row: Logo + Brand */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 14,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <AuroraLogoMark size={18} />
            <span
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontSize: 11,
                opacity: 0.5,
                textTransform: "uppercase",
                letterSpacing: "0.15em",
              }}
            >
              {BRAND.name}
            </span>
          </div>

          {/* Current Tab Title + Engine Status */}
          <div style={{ textAlign: "right" }}>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontSize: 16,
                fontWeight: 500,
                background: gradients.lavenderGlow,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}
            >
              Betül Console
            </div>
            {engineStatus && (
              <div
                style={{
                  fontSize: 9,
                  color: engineStatus.llm_enabled ? "#4ade80" : colors.textMuted,
                  marginTop: 2,
                  fontFamily: "'JetBrains Mono', monospace",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "flex-end",
                  gap: 4,
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "50%",
                    background: engineStatus.llm_enabled ? "#4ade80" : "#ef4444",
                    display: "inline-block",
                  }}
                />
                {engineStatus.model} · {engineStatus.mode}
              </div>
            )}
          </div>
        </div>

        {/* Tab Switcher */}
        <div
          style={{
            display: "flex",
            gap: 8,
            justifyContent: "center",
          }}
        >
          {TABS.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            />
          ))}
        </div>
      </header>

      {/* Tab Content */}
      {activeTab === "operator" ? (
        <OperatorConsole />
      ) : activeTab === "state" ? (
        <StateDashboard />
      ) : (
        <div style={{ minHeight: "calc(100vh - 200px)" }}>
          {activeTab === "inbox" && <InboxTab />}
          {activeTab === "story" && <TimelineTab />}
          {activeTab === "stats" && <VibeDashboard />}
        </div>
      )}

      {/* Footer */}
      <footer
        style={{
          padding: "24px 20px",
          textAlign: "center",
          borderTop: `1px solid ${colors.borderSubtle}`,
        }}
      >
        <div
          style={{
            fontFamily: "'Playfair Display', serif",
            fontStyle: "italic",
            fontSize: 12,
            color: colors.auroraLavender,
            opacity: 0.6,
            marginBottom: 8,
          }}
        >
          "{BRAND.tagline}"
        </div>
        <div
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 10,
            opacity: 0.3,
            letterSpacing: "0.05em",
          }}
        >
          Dedicated to Betül ✨
        </div>
      </footer>
    </div>
  );
}

export default App;
