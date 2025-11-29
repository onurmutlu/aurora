/**
 * AuroraOS UI Kit — Button Component
 */

import { ReactNode, ButtonHTMLAttributes } from "react";
import { colors, gradients, shadows } from "../../brand/colors";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  icon?: ReactNode;
  children: ReactNode;
}

const variants = {
  primary: {
    background: gradients.lavenderGlow,
    color: "#000000",
    border: "none",
    boxShadow: shadows.button,
  },
  secondary: {
    background: "rgba(255, 255, 255, 0.05)",
    color: colors.textPrimary,
    border: `1px solid ${colors.borderLight}`,
    boxShadow: "none",
  },
  ghost: {
    background: "transparent",
    color: colors.textSecondary,
    border: "none",
    boxShadow: "none",
  },
  danger: {
    background: "rgba(239, 68, 68, 0.1)",
    color: "#EF4444",
    border: "1px solid rgba(239, 68, 68, 0.3)",
    boxShadow: "none",
  },
};

const sizes = {
  sm: {
    padding: "6px 12px",
    fontSize: "12px",
    borderRadius: "6px",
    gap: "6px",
  },
  md: {
    padding: "10px 18px",
    fontSize: "14px",
    borderRadius: "8px",
    gap: "8px",
  },
  lg: {
    padding: "14px 24px",
    fontSize: "16px",
    borderRadius: "10px",
    gap: "10px",
  },
};

export function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  icon,
  children,
  disabled,
  style,
  ...props
}: ButtonProps) {
  const variantStyles = variants[variant];
  const sizeStyles = sizes[size];

  return (
    <button
      disabled={disabled}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: sizeStyles.gap,
        padding: sizeStyles.padding,
        fontSize: sizeStyles.fontSize,
        fontFamily: "'Inter', sans-serif",
        fontWeight: 500,
        borderRadius: sizeStyles.borderRadius,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        width: fullWidth ? "100%" : "auto",
        transition: "all 0.2s ease",
        ...variantStyles,
        ...style,
      }}
      {...props}
    >
      {icon && <span style={{ display: "flex" }}>{icon}</span>}
      {children}
    </button>
  );
}

