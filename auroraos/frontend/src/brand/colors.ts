/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Brand Colors                                          ║
 * ║   "From the void, her light."                                    ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

// Primary Palette
export const colors = {
  // Primary
  onyxBlack: "#000000",
  auroraLavender: "#AFA3FF",
  deepVoidGray: "#111111",
  
  // Secondary
  roseMist: "#F7D6FF",
  silverPulse: "#CFCFCF",
  softPlasma: "#B8A7F9",
  
  // Accent (AI / State)
  femmeViolet: "#AD5FFF",
  neuralMint: "#00F5A0",
  
  // Neutrals
  void: "#0A0A0A",
  midnight: "#1A1A1A",
  charcoal: "#2A2A2A",
  
  // Text
  textPrimary: "#FFFFFF",
  textSecondary: "rgba(255, 255, 255, 0.7)",
  textMuted: "rgba(255, 255, 255, 0.4)",
  
  // Borders
  borderSubtle: "rgba(255, 255, 255, 0.08)",
  borderLight: "rgba(255, 255, 255, 0.12)",
  borderActive: "rgba(175, 163, 255, 0.5)",
} as const;

// Gradients
export const gradients = {
  auroraHalo: "radial-gradient(circle at 50% 50%, rgba(175, 163, 255, 0.15) 0%, transparent 70%)",
  voidBackground: "linear-gradient(180deg, #000000 0%, #0A0A0A 50%, #111111 100%)",
  lavenderGlow: "linear-gradient(135deg, #AFA3FF 0%, #AD5FFF 100%)",
  mintAccent: "linear-gradient(135deg, #00F5A0 0%, #00D9A0 100%)",
  cardSurface: "linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)",
} as const;

// Shadows
export const shadows = {
  glow: "0 0 60px rgba(175, 163, 255, 0.15)",
  card: "0 4px 24px rgba(0, 0, 0, 0.4)",
  button: "0 2px 12px rgba(175, 163, 255, 0.2)",
} as const;

export type ColorKey = keyof typeof colors;
export type GradientKey = keyof typeof gradients;

