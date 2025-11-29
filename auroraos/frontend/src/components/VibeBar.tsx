/**
 * AuroraOS — Vibe Mode Selector
 * "From the void, her light."
 */

import { useState } from "react";
import { updateVibe } from "../api";
import { colors } from "../brand/colors";
import { VIBE_MODES } from "../brand";

interface Props {
  onModeChange?: (mode: string) => void;
}

export function VibeBar({ onModeChange }: Props) {
  const [mode, setMode] = useState<string>("soft_femme");
  const [energy, setEnergy] = useState<number>(75);

  async function handleChange(newMode: string) {
    setMode(newMode);
    onModeChange?.(newMode);
    try {
      await updateVibe({
        current_mode: newMode,
        energy_level: energy,
      });
    } catch (e) {
      console.error("Vibe update failed:", e);
    }
  }

  return (
    <div
      style={{
        padding: "16px 20px",
        borderBottom: `1px solid ${colors.borderSubtle}`,
        background: "rgba(0, 0, 0, 0.3)",
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 10,
          opacity: 0.4,
          marginBottom: 12,
          textTransform: "uppercase",
          letterSpacing: "0.15em",
        }}
      >
        Vibe Mode
      </div>
      
      <div
        style={{
          display: "flex",
          gap: 8,
          overflowX: "auto",
          paddingBottom: 4,
          marginBottom: 16,
        }}
      >
        {VIBE_MODES.map((m) => {
          const isActive = m.id === mode;
          return (
            <button
              key={m.id}
              onClick={() => handleChange(m.id)}
              style={{
                padding: "10px 16px",
                borderRadius: 999,
                border: isActive 
                  ? `1px solid ${colors.auroraLavender}` 
                  : `1px solid ${colors.borderLight}`,
                fontSize: 12,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 500,
                cursor: "pointer",
                backgroundColor: isActive 
                  ? "rgba(175, 163, 255, 0.15)" 
                  : "rgba(255, 255, 255, 0.03)",
                color: isActive 
                  ? colors.auroraLavender 
                  : colors.textSecondary,
                whiteSpace: "nowrap",
                transition: "all 0.2s ease",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span style={{ fontSize: 14 }}>{m.emoji}</span>
              <span>{m.label}</span>
            </button>
          );
        })}
      </div>
      
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
        }}
      >
        <span 
          style={{ 
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 10, 
            opacity: 0.4,
            textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}
        >
          Energy
        </span>
        <div style={{ flex: 1, position: "relative" }}>
          <div
            style={{
              position: "absolute",
              left: 0,
              top: "50%",
              transform: "translateY(-50%)",
              height: 4,
              width: `${energy}%`,
              background: `linear-gradient(90deg, ${colors.auroraLavender}, ${colors.femmeViolet})`,
              borderRadius: 999,
              pointerEvents: "none",
            }}
          />
          <input
            type="range"
            min={0}
            max={100}
            value={energy}
            onChange={(e) => setEnergy(Number(e.target.value))}
            style={{
              width: "100%",
              background: "rgba(255, 255, 255, 0.08)",
            }}
          />
        </div>
        <span 
          style={{ 
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 12, 
            minWidth: 40,
            textAlign: "right",
            color: colors.auroraLavender,
          }}
        >
          {energy}%
        </span>
      </div>
    </div>
  );
}
