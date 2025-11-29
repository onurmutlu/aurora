/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS State Dashboard — Government Control Panel            ║
 * ║   "The sovereign view of the digital nation"                     ║
 * ║                                                                  ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React, { useState, useEffect } from 'react';
import { fetchDashboardStats, fetchAIOperations, type DashboardStats, type AIOperation } from './api';

// Icons (inline SVG components)
const Globe = ({ size = 20, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}>
    <circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
  </svg>
);

const Building2 = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>
  </svg>
);

const Gavel = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m14.5 12.5-8 8a2.119 2.119 0 1 1-3-3l8-8"/><path d="m16 16 6-6"/><path d="m8 8 6-6"/><path d="m9 7 8 8"/><path d="m21 11-8-8"/>
  </svg>
);

const Radio = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/><path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/>
  </svg>
);

const Search = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
  </svg>
);

const Fingerprint = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 10a2 2 0 0 0-2 2c0 1.02-.1 2.51-.26 4"/><path d="M14 13.12c0 2.38 0 6.38-1 8.88"/><path d="M17.29 21.02c.12-.6.43-2.3.5-3.02"/><path d="M2 12a10 10 0 0 1 18-6"/><path d="M2 16h.01"/><path d="M21.8 16c.2-2 .131-5.354 0-6"/><path d="M5 19.5C5.5 18 6 15 6 12a6 6 0 0 1 .34-2"/><path d="M8.65 22c.21-.66.45-1.32.57-2"/><path d="M9 6.8a6 6 0 0 1 9 5.2v2"/>
  </svg>
);

const Activity = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
  </svg>
);

const AlertTriangle = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>
  </svg>
);

// --- DEFAULT/FALLBACK DATA ---
const DEFAULT_STATS: DashboardStats = {
  citizens: { total: 0, verified: 0, pending: 0, online: 0, banned: 0, new_today: 0, basic_count: 0, silver_count: 0, gold_count: 0, platinum_count: 0, founder_count: 0 },
  treasury: { reserve: '0 NCR', reserve_raw: 0, gdp_24h: '0%', gdp_raw: 0, inflation: '0%', inflation_raw: 0, liquidity: 'Low', transactions_24h: 0, volume_24h: 0, avg_transaction: 0 },
  threat: { level: 'LOW', active_threats: 0, mitigated_24h: 0, last_incident: null, details: '0 Cyber-Attacks detected' },
  ai_operations_24h: 0,
  flagged_content: 0,
};

export const StateDashboard: React.FC = () => {
  const [activeModule, setActiveModule] = useState('TREASURY');
  const [stats, setStats] = useState<DashboardStats>(DEFAULT_STATS);
  const [aiOps, setAiOps] = useState<AIOperation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [dashboardData, aiOpsData] = await Promise.all([
          fetchDashboardStats(),
          fetchAIOperations({ limit: 10 }),
        ]);
        setStats(dashboardData);
        setAiOps(aiOpsData);
      } catch (err) {
        console.error('Failed to load state data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
    const interval = setInterval(loadData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  return (
    <div 
      style={{
        minHeight: '100vh',
        background: '#020617',
        color: '#cbd5e1',
        fontFamily: 'ui-monospace, monospace',
        fontSize: 14,
        display: 'flex',
        overflow: 'hidden',
      }}
    >
      
      {/* 1. STATE SIDEBAR (BAKANLIKLAR) */}
      <aside 
        style={{
          width: 256,
          borderRight: '1px solid #1e293b',
          background: '#0f172a',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div 
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            padding: '0 24px',
            borderBottom: '1px solid #1e293b',
            gap: 12,
          }}
        >
          <div 
            style={{
              width: 24,
              height: 24,
              background: '#06b6d4',
              borderRadius: 4,
              animation: 'pulse 2s infinite',
            }}
          />
          <h1 style={{ fontWeight: 700, color: 'white', letterSpacing: '0.1em', margin: 0 }}>
            AURORA<span style={{ color: '#06b6d4' }}>.OS</span>
          </h1>
        </div>

        <nav style={{ flex: 1, padding: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#64748b', marginBottom: 8, padding: '0 8px' }}>
            GOVERNMENT MODULES
          </div>
          
          <ModuleButton 
            icon={<Building2 />}
            label="TREASURY & IMF"
            active={activeModule === 'TREASURY'}
            onClick={() => setActiveModule('TREASURY')}
          />
          
          <ModuleButton 
            icon={<Fingerprint />}
            label="CITIZEN REGISTRY"
            active={activeModule === 'CITIZEN'}
            onClick={() => setActiveModule('CITIZEN')}
          />
          
          <ModuleButton 
            icon={<Gavel />}
            label="LAW & MODERATION"
            active={activeModule === 'JUSTICE'}
            onClick={() => setActiveModule('JUSTICE')}
          />
          
          <ModuleButton 
            icon={<Radio />}
            label="AI OPS / COMMS"
            active={activeModule === 'COMMS'}
            onClick={() => setActiveModule('COMMS')}
          />
        </nav>

        <div style={{ padding: 16, borderTop: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 11, color: '#64748b' }}>
            <div style={{ width: 8, height: 8, background: '#22c55e', borderRadius: '50%' }} />
            SYSTEM STATUS: ONLINE
          </div>
          <div style={{ marginTop: 8, fontSize: 10, color: '#475569' }}>
            KERNEL v4.2.0 | LATENCY: 12ms
          </div>
        </div>
      </aside>

      {/* 2. MAIN STATE VIEW */}
      <main 
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'6\' height=\'6\' viewBox=\'0 0 6 6\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%23334155\' fill-opacity=\'0.1\'%3E%3Cpath d=\'M5 0h1L0 6V5zM6 5v1H5z\'/%3E%3C/g%3E%3C/svg%3E")',
        }}
      >
        
        {/* HEADER */}
        <header 
          style={{
            height: 64,
            borderBottom: '1px solid #1e293b',
            background: 'rgba(2, 6, 23, 0.9)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 32px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Globe size={20} className="text-slate-500" />
            <span style={{ color: 'white', fontWeight: 700 }}>TERRITORY: GLOBAL</span>
            <span style={{ color: '#475569' }}>|</span>
            <span style={{ color: '#06b6d4' }}>POPULATION: {stats.citizens.total.toLocaleString()}</span>
          </div>
          <div 
            style={{
              display: 'flex',
              alignItems: 'center',
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 4,
              padding: '6px 12px',
              width: 384,
            }}
          >
            <Search />
            <input 
              type="text" 
              placeholder="Search Citizen ID / Transaction Hash..." 
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'white',
                width: '100%',
                fontSize: 12,
                marginLeft: 8,
              }}
            />
          </div>
        </header>

        {/* DASHBOARD CONTENT */}
        <div 
          style={{
            padding: 32,
            display: 'grid',
            gridTemplateColumns: 'repeat(12, 1fr)',
            gap: 24,
            height: 'calc(100vh - 64px)',
            overflowY: 'auto',
          }}
        >
            
          {/* TOP METRICS ROW */}
          <MetricCard 
            label="NATIONAL RESERVE"
            value={stats.treasury.reserve}
            progress={Math.min(100, (stats.treasury.reserve_raw / 5000000) * 100)}
          />
          <MetricCard 
            label="GDP GROWTH (24H)"
            value={stats.treasury.gdp_24h}
            valueColor={stats.treasury.gdp_raw >= 0 ? "#4ade80" : "#ef4444"}
            subtitle="Target: +15%"
          />
          <MetricCard 
            label="ACTIVE CITIZENS"
            value={stats.citizens.online.toString()}
            dots={3}
          />
          <MetricCard 
            label="THREAT LEVEL"
            value={stats.threat.level}
            valueColor={stats.threat.level === "LOW" ? "#4ade80" : stats.threat.level === "MEDIUM" ? "#fbbf24" : "#ef4444"}
            subtitle={stats.threat.details}
            danger={stats.threat.level !== "LOW"}
          />

          {/* CENTRAL MAP / HEATMAP */}
          <div 
            style={{
              gridColumn: 'span 8',
              background: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: 4,
              position: 'relative',
              overflow: 'hidden',
              minHeight: 400,
            }}
          >
            <div 
              style={{
                position: 'absolute',
                top: 16,
                left: 16,
                zIndex: 10,
                background: 'rgba(0,0,0,0.5)',
                backdropFilter: 'blur(4px)',
                padding: '4px 12px',
                border: '1px solid #334155',
                fontSize: 11,
              }}
            >
              VIEW: LIQUIDITY HEATMAP
            </div>
            {/* Abstract Map Grid */}
            <div 
              style={{
                width: '100%',
                height: '100%',
                display: 'grid',
                gridTemplateColumns: 'repeat(12, 1fr)',
                gridTemplateRows: 'repeat(6, 1fr)',
                opacity: 0.2,
              }}
            >
              {[...Array(72)].map((_, i) => (
                <div 
                  key={i} 
                  style={{
                    border: '1px solid rgba(6, 182, 212, 0.3)',
                    background: Math.random() > 0.8 ? 'rgba(6, 182, 212, 0.4)' : 'transparent',
                  }}
                />
              ))}
            </div>
            <div 
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                pointerEvents: 'none',
              }}
            >
              <div 
                style={{
                  color: '#334155',
                  fontSize: 48,
                  fontWeight: 700,
                  opacity: 0.2,
                }}
              >
                DELTA NOVA
              </div>
            </div>
          </div>

          {/* RIGHT SIDE: AI OPS / LAW */}
          <div 
            style={{
              gridColumn: 'span 4',
              display: 'flex',
              flexDirection: 'column',
              gap: 24,
            }}
          >
            
            {/* AI COMMS TERMINAL */}
            <div 
              style={{
                background: '#020617',
                border: '1px solid #1e293b',
                borderRadius: 4,
                padding: 16,
                flex: 1,
              }}
            >
              <div 
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 16,
                  paddingBottom: 8,
                  borderBottom: '1px solid #1e293b',
                }}
              >
                <span 
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: '#06b6d4',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                  }}
                >
                  <Activity /> AI OPERATOR FEED
                </span>
                <span style={{ fontSize: 10, color: '#64748b' }}>LIVE</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {aiOps.length === 0 ? (
                  <div style={{ fontSize: 11, color: '#64748b', textAlign: 'center', padding: '20px 0' }}>
                    {loading ? 'Loading...' : 'No recent operations'}
                  </div>
                ) : (
                  aiOps.slice(0, 5).map(op => (
                    <div 
                      key={op.id} 
                      style={{
                        fontSize: 12,
                        fontFamily: 'ui-monospace, monospace',
                        borderLeft: '2px solid #334155',
                        paddingLeft: 12,
                        paddingTop: 4,
                        paddingBottom: 4,
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8' }}>
                        <span>{op.type}</span>
                        <span style={{ 
                          color: op.status === 'COMPLETED' ? '#22c55e' : 
                                 op.status === 'FAILED' ? '#ef4444' : 
                                 op.status === 'IN_PROGRESS' ? '#fbbf24' : '#94a3b8' 
                        }}>
                          {op.status}
                        </span>
                      </div>
                      <div style={{ color: 'white', marginTop: 4 }}>{op.target}</div>
                      <div style={{ fontSize: 10, color: '#475569', marginTop: 4 }}>
                        {op.duration_seconds ? `${op.duration_seconds}s` : op.sentiment || 'Pending...'}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* MODERATION QUEUE */}
            <div 
              style={{
                background: 'rgba(15, 23, 42, 0.5)',
                border: '1px solid #1e293b',
                borderRadius: 4,
                padding: 16,
              }}
            >
              <div 
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: '#94a3b8',
                  marginBottom: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                <AlertTriangle /> FLAGGED CONTENT
              </div>
              <div 
                style={{
                  textAlign: 'center',
                  padding: '32px 0',
                  color: '#475569',
                  fontSize: 12,
                }}
              >
                {stats.flagged_content === 0 ? (
                  <>All systems nominal. <br/> No manual review needed.</>
                ) : (
                  <span style={{ color: '#fbbf24' }}>
                    {stats.flagged_content} items pending review
                  </span>
                )}
              </div>
              <button 
                style={{
                  width: '100%',
                  padding: '8px 0',
                  background: '#1e293b',
                  color: '#cbd5e1',
                  fontSize: 12,
                  border: '1px solid #475569',
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#334155'}
                onMouseLeave={(e) => e.currentTarget.style.background = '#1e293b'}
              >
                VIEW ARCHIVE
              </button>
            </div>
          </div>
        </div>
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

// Helper Components
interface ModuleButtonProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

const ModuleButton: React.FC<ModuleButtonProps> = ({ icon, label, active, onClick }) => (
  <button 
    onClick={onClick}
    style={{
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: '12px',
      borderRadius: 4,
      background: active ? 'rgba(8, 145, 178, 0.2)' : 'transparent',
      color: active ? '#06b6d4' : '#cbd5e1',
      border: active ? '1px solid rgba(6, 182, 212, 0.3)' : '1px solid transparent',
      cursor: 'pointer',
      transition: 'all 0.2s',
      fontSize: 13,
    }}
    onMouseEnter={(e) => {
      if (!active) e.currentTarget.style.background = '#1e293b';
    }}
    onMouseLeave={(e) => {
      if (!active) e.currentTarget.style.background = 'transparent';
    }}
  >
    {icon}
    <span>{label}</span>
  </button>
);

interface MetricCardProps {
  label: string;
  value: string;
  valueColor?: string;
  subtitle?: string;
  progress?: number;
  dots?: number;
  danger?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  label, 
  value, 
  valueColor = 'white', 
  subtitle, 
  progress, 
  dots,
  danger 
}) => (
  <div 
    style={{
      gridColumn: 'span 3',
      background: danger ? 'rgba(127, 29, 29, 0.1)' : 'rgba(15, 23, 42, 0.5)',
      border: danger ? '1px solid rgba(127, 29, 29, 0.3)' : '1px solid #1e293b',
      padding: 20,
      borderRadius: 4,
    }}
  >
    <div style={{ fontSize: 11, color: danger ? '#f87171' : '#64748b', marginBottom: 4 }}>
      {label}
    </div>
    <div 
      style={{ 
        fontSize: 24, 
        color: valueColor, 
        fontWeight: 700, 
        fontFamily: 'ui-monospace, monospace',
        letterSpacing: '-0.05em',
      }}
    >
      {value}
    </div>
    {progress !== undefined && (
      <div style={{ marginTop: 8, height: 4, width: '100%', background: '#1e293b' }}>
        <div style={{ width: `${progress}%`, height: '100%', background: '#0891b2' }} />
      </div>
    )}
    {dots !== undefined && (
      <div style={{ display: 'flex', gap: 4, marginTop: 8 }}>
        {[...Array(dots)].map((_, i) => (
          <span 
            key={i} 
            style={{ 
              width: 8, 
              height: 8, 
              background: '#22c55e', 
              borderRadius: '50%',
              opacity: i === dots - 1 ? 0.5 : 1,
            }} 
          />
        ))}
      </div>
    )}
    {subtitle && (
      <div style={{ fontSize: 11, color: danger ? 'rgba(127, 29, 29, 0.6)' : '#475569', marginTop: 8 }}>
        {subtitle}
      </div>
    )}
  </div>
);

export default StateDashboard;

