/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Typography System                                     ║
 * ║   Display: Space Grotesk | Body: Inter | Code: JetBrains Mono   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

export const fonts = {
  display: "'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif",
  body: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  code: "'JetBrains Mono', 'SF Mono', Consolas, monospace",
  signature: "'Playfair Display', Georgia, serif",
} as const;

export const fontSizes = {
  xs: "10px",
  sm: "12px",
  md: "14px",
  lg: "16px",
  xl: "20px",
  "2xl": "24px",
  "3xl": "32px",
  "4xl": "48px",
  "5xl": "64px",
} as const;

export const fontWeights = {
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const;

export const lineHeights = {
  tight: 1.2,
  normal: 1.5,
  relaxed: 1.7,
} as const;

export const letterSpacing = {
  tight: "-0.02em",
  normal: "0",
  wide: "0.05em",
  wider: "0.1em",
  widest: "0.2em",
} as const;

