/**
 * AuroraOS UI Kit — Card Component
 */

import { ReactNode, CSSProperties } from "react";
import { colors, gradients, shadows } from "../../brand/colors";

interface CardProps {
  children: ReactNode;
  variant?: "default" | "elevated" | "outlined";
  padding?: "none" | "sm" | "md" | "lg";
  style?: CSSProperties;
}

const paddings = {
  none: "0",
  sm: "12px",
  md: "16px",
  lg: "24px",
};

export function Card({
  children,
  variant = "default",
  padding = "md",
  style,
}: CardProps) {
  const baseStyles: CSSProperties = {
    borderRadius: "16px",
    padding: paddings[padding],
    transition: "all 0.2s ease",
  };

  const variantStyles: Record<string, CSSProperties> = {
    default: {
      background: gradients.cardSurface,
      border: `1px solid ${colors.borderSubtle}`,
      backdropFilter: "blur(10px)",
    },
    elevated: {
      background: "rgba(0, 0, 0, 0.6)",
      border: `1px solid ${colors.borderSubtle}`,
      boxShadow: shadows.card,
      backdropFilter: "blur(20px)",
    },
    outlined: {
      background: "transparent",
      border: `1px solid ${colors.borderLight}`,
    },
  };

  return (
    <div
      style={{
        ...baseStyles,
        ...variantStyles[variant],
        ...style,
      }}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: 16,
      }}
    >
      <div>
        <div
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 16,
            fontWeight: 500,
            color: colors.textPrimary,
          }}
        >
          {title}
        </div>
        {subtitle && (
          <div
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 12,
              color: colors.textMuted,
              marginTop: 4,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

