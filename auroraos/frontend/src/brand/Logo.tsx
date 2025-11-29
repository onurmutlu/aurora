/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Logo — "Aura Halo"                                    ║
 * ║   Broken circle = human touch                                    ║
 * ║   Dedicated to Betül                                             ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

interface LogoProps {
  size?: number;
  color?: string;
  animated?: boolean;
}

export function AuroraLogo({ 
  size = 80, 
  color = "#AFA3FF",
  animated = false 
}: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{
        animation: animated ? "auroraRotate 20s linear infinite" : undefined,
      }}
    >
      <defs>
        <linearGradient id="auroraGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="1" />
          <stop offset="50%" stopColor="#AD5FFF" stopOpacity="0.8" />
          <stop offset="100%" stopColor={color} stopOpacity="0.6" />
        </linearGradient>
        <filter id="auroraGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      
      {/* Outer Halo - Broken Circle */}
      <path
        d="M 50 5 
           A 45 45 0 1 1 20 15"
        stroke="url(#auroraGradient)"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
        filter="url(#auroraGlow)"
      />
      
      {/* Inner subtle circle */}
      <circle
        cx="50"
        cy="50"
        r="30"
        stroke={color}
        strokeWidth="0.5"
        strokeOpacity="0.3"
        fill="none"
      />
      
      {/* Center dot - the aura core */}
      <circle
        cx="50"
        cy="50"
        r="3"
        fill={color}
        opacity="0.8"
      />
      
      <style>
        {`
          @keyframes auroraRotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </svg>
  );
}

export function AuroraLogoMark({ size = 24 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M 12 2 A 10 10 0 1 1 5 4"
        stroke="#AFA3FF"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="12" cy="12" r="2" fill="#AFA3FF" />
    </svg>
  );
}

export function AuroraWordmark({ height = 24 }: { height?: number }) {
  const width = height * 5;
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 120 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <text
        x="0"
        y="18"
        fontFamily="'Space Grotesk', sans-serif"
        fontSize="18"
        fontWeight="500"
        fill="#FFFFFF"
        letterSpacing="0.05em"
      >
        AURORAOS
      </text>
    </svg>
  );
}

