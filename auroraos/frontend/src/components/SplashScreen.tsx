/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Splash Screen                                         ║
 * ║   "From the void, her light."                                    ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import { useState, useEffect } from "react";
import { AuroraLogo } from "../brand/Logo";
import { colors, gradients } from "../brand/colors";

interface SplashScreenProps {
  onComplete?: () => void;
  duration?: number;
}

export function SplashScreen({ onComplete, duration = 3000 }: SplashScreenProps) {
  const [phase, setPhase] = useState<"enter" | "show" | "exit">("enter");
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Enter phase
    const enterTimer = setTimeout(() => setPhase("show"), 100);
    
    // Exit phase
    const exitTimer = setTimeout(() => {
      setPhase("exit");
    }, duration - 500);

    // Complete
    const completeTimer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, duration);

    return () => {
      clearTimeout(enterTimer);
      clearTimeout(exitTimer);
      clearTimeout(completeTimer);
    };
  }, [duration, onComplete]);

  if (!visible) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: gradients.voidBackground,
        opacity: phase === "enter" ? 0 : phase === "exit" ? 0 : 1,
        transition: "opacity 0.5s ease-in-out",
      }}
    >
      {/* Ambient Halo Glow */}
      <div
        style={{
          position: "absolute",
          width: "400px",
          height: "400px",
          background: gradients.auroraHalo,
          borderRadius: "50%",
          opacity: phase === "show" ? 0.6 : 0,
          transition: "opacity 1s ease-in-out",
          pointerEvents: "none",
        }}
      />

      {/* Logo */}
      <div
        style={{
          transform: phase === "show" ? "scale(1)" : "scale(0.9)",
          opacity: phase === "show" ? 1 : 0,
          transition: "all 0.8s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        <AuroraLogo size={100} animated />
      </div>

      {/* Brand Name */}
      <div
        style={{
          marginTop: 32,
          opacity: phase === "show" ? 1 : 0,
          transform: phase === "show" ? "translateY(0)" : "translateY(10px)",
          transition: "all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s",
        }}
      >
        <div
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 28,
            fontWeight: 500,
            letterSpacing: "0.15em",
            color: colors.textPrimary,
          }}
        >
          AURORAOS
        </div>
        <div
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 12,
            fontWeight: 400,
            letterSpacing: "0.1em",
            color: colors.textMuted,
            textAlign: "center",
            marginTop: 8,
          }}
        >
          Betül Aura Intelligence
        </div>
      </div>

      {/* Tagline */}
      <div
        style={{
          position: "absolute",
          bottom: 100,
          opacity: phase === "show" ? 1 : 0,
          transform: phase === "show" ? "translateY(0)" : "translateY(10px)",
          transition: "all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.4s",
        }}
      >
        <div
          style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: 14,
            fontStyle: "italic",
            color: colors.auroraLavender,
            opacity: 0.8,
          }}
        >
          "Your aura is the system."
        </div>
      </div>

      {/* Launch hint */}
      <div
        style={{
          position: "absolute",
          bottom: 50,
          opacity: phase === "show" ? 0.4 : 0,
          transition: "opacity 1s ease-in-out 1s",
        }}
      >
        <div
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 11,
            letterSpacing: "0.2em",
            color: colors.textMuted,
            textTransform: "uppercase",
          }}
        >
          ⤑ launch
        </div>
      </div>
    </div>
  );
}

