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
        padding: "10px 16px",
        borderBottom: `1px solid ${colors.borderSubtle}`,
        background: "rgba(0, 0, 0, 0.3)",
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontFamily: "'Space Grotesk', sans-serif",
          fontSize: 9,
          opacity: 0.4,
          marginBottom: 8,
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        Vibe Mode
      </div>
      
      <div
        style={{
          display: "flex",
          gap: 6,
          overflowX: "auto",
          paddingBottom: 2,
          marginBottom: 10,
        }}
      >
        {VIBE_MODES.map((m) => {
          const isActive = m.id === mode;
          return (
            <button
              key={m.id}
              onClick={() => handleChange(m.id)}
              style={{
                padding: "5px 10px",
                borderRadius: 12,
                border: isActive 
                  ? `1px solid ${colors.auroraLavender}` 
                  : `1px solid ${colors.borderLight}`,
                fontSize: 10,
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
                gap: 4,
              }}
            >
              <span style={{ fontSize: 11 }}>{m.emoji}</span>
              <span>{m.label}</span>
            </button>
          );
        })}
      </div>
      
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span 
          style={{ 
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 9, 
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
              height: 3,
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
              height: 3,
            }}
          />
        </div>
        <span 
          style={{ 
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 10, 
            minWidth: 32,
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
