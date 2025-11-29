/**
 * AuroraOS UI Kit — Badge Component
 */

import { ReactNode } from "react";
import { colors } from "../../brand/colors";

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "aurora" | "mint" | "muted";
  size?: "sm" | "md";
}

const variants = {
  default: {
    background: "rgba(255, 255, 255, 0.1)",
    color: colors.textSecondary,
    border: "none",
  },
  aurora: {
    background: "rgba(175, 163, 255, 0.15)",
    color: colors.auroraLavender,
    border: "1px solid rgba(175, 163, 255, 0.3)",
  },
  mint: {
    background: "rgba(0, 245, 160, 0.1)",
    color: colors.neuralMint,
    border: "1px solid rgba(0, 245, 160, 0.3)",
  },
  muted: {
    background: "rgba(255, 255, 255, 0.05)",
    color: colors.textMuted,
    border: "none",
  },
};

const sizes = {
  sm: {
    padding: "2px 6px",
    fontSize: "10px",
  },
  md: {
    padding: "4px 10px",
    fontSize: "12px",
  },
};

export function Badge({
  children,
  variant = "default",
  size = "sm",
}: BadgeProps) {
  const variantStyles = variants[variant];
  const sizeStyles = sizes[size];

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
        padding: sizeStyles.padding,
        fontSize: sizeStyles.fontSize,
        fontFamily: "'Inter', sans-serif",
        fontWeight: 500,
        borderRadius: "999px",
        textTransform: "uppercase",
        letterSpacing: "0.02em",
        whiteSpace: "nowrap",
        ...variantStyles,
      }}
    >
      {children}
    </span>
  );
}

