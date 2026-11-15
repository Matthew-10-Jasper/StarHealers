import React, { useEffect, useState } from 'react';
import { Shield, Radio, Activity, AlertTriangle, RefreshCw, Cpu, Brain, Sun } from 'lucide-react';
import { OperationalState, QualityStatus } from '../types/mission';

export type ActiveModuleType = 'MODULE_4' | 'MODULE_6' | 'MODULE_7';

interface HeaderProps {
  operationalState: OperationalState;
  missionName: string;
  contextVersion: number;
  dataQuality: QualityStatus;
  wsConnected: boolean;
  onRefresh: () => void;
  isLoading: boolean;
  activeModule: ActiveModuleType;
  onSelectModule: (module: ActiveModuleType) => void;
}

export const Header: React.FC<HeaderProps> = ({
  operationalState,
  missionName,
  contextVersion,
  dataQuality,
  wsConnected,
  onRefresh,
  isLoading,
  activeModule,
  onSelectModule
}) => {
  const [elapsedTime, setElapsedTime] = useState('00d 00h 00m 00s');

  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      const now = Date.now();
      const diff = Math.floor((now - start) / 1000);
      const days = Math.floor(diff / 86400).toString().padStart(2, '0');
      const hours = Math.floor((diff % 86400) / 3600).toString().padStart(2, '0');
      const mins = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
      const secs = (diff % 60).toString().padStart(2, '0');
      setElapsedTime(`${days}d ${hours}h ${mins}m ${secs}s`);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const getStateBadge = (state: OperationalState) => {
    switch (state) {
      case 'NOMINAL':
        return 'bg-emerald-950/60 text-emerald-400 border-emerald-600/50 shadow-emerald-900/20';
      case 'DEGRADED':
        return 'bg-amber-950/60 text-amber-400 border-amber-500/60 shadow-amber-900/30';
      case 'CONTINGENCY':
        return 'bg-crimson-950/80 text-crimson-400 border-crimson-500 shadow-crimson-900/40 animate-pulse';
      case 'RECOVERY':
        return 'bg-cyan-950/60 text-cyan-400 border-cyan-500/60 shadow-cyan-900/30';
      case 'UNKNOWN':
      default:
        return 'bg-slate-900 text-slate-300 border-slate-600 shadow-slate-900/20';
    }
  };

  return (
    <header className="border-b border-[#1E293B] bg-[#0F172A]/90 backdrop-blur-md px-4 sm:px-6 py-3.5 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Starhealers Module Branding */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-indigo-500/20 via-sky-500/20 to-amber-500/20 border border-slate-700 flex items-center justify-center">
            {activeModule === 'MODULE_4' ? (
              <Cpu className="h-5 w-5 text-crimson-400" />
            ) : activeModule === 'MODULE_6' ? (
              <Brain className="h-5 w-5 text-[#6366F1]" />
            ) : (
              <Sun className="h-5 w-5 text-[#EAB308]" />
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs tracking-widest text-[#38BDF8] uppercase font-semibold">
                STARHEALERS • UNIFIED PLATFORM
              </span>
              <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                CTX v{contextVersion}
              </span>
            </div>
            <h1 className="text-base sm:text-lg font-bold text-[#F8FAFC] tracking-tight">
              {activeModule === 'MODULE_4' && 'Mission Environment Intelligence & Adaptive Context'}
              {activeModule === 'MODULE_6' && 'Circadian Rhythm, Fatigue & Psychomotor Stress (M6)'}
              {activeModule === 'MODULE_7' && 'Space Environment, Radiation & Life Support (M7)'}
            </h1>
          </div>
        </div>

        {/* Center: Module Navigation Pills */}
        <div className="flex items-center space-x-1.5 bg-[#060913] p-1 rounded-xl border border-[#1E293B] self-center">
          <button
            onClick={() => onSelectModule('MODULE_4')}
            className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all flex items-center space-x-1.5 ${
              activeModule === 'MODULE_4'
                ? 'bg-crimson-500/20 text-crimson-400 border border-crimson-500/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="h-3.5 w-3.5" />
            <span>M4: MISSION</span>
          </button>

          <button
            onClick={() => onSelectModule('MODULE_6')}
            className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all flex items-center space-x-1.5 ${
              activeModule === 'MODULE_6'
                ? 'bg-[#6366F1]/20 text-[#38BDF8] border border-[#6366F1]/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Brain className="h-3.5 w-3.5" />
            <span>M6: CIRCADIAN</span>
          </button>

          <button
            onClick={() => onSelectModule('MODULE_7')}
            className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all flex items-center space-x-1.5 ${
              activeModule === 'MODULE_7'
                ? 'bg-[#EAB308]/20 text-[#EAB308] border border-[#EAB308]/50 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sun className="h-3.5 w-3.5" />
            <span>M7: ENVIRONMENT</span>
          </button>
        </div>

        {/* Right: Operational State & Status Badges */}
        <div className="flex items-center space-x-3 self-end md:self-auto">
          {/* WebSocket Status */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#060913] border border-[#1E293B] text-xs font-mono">
            <Radio className={`h-3.5 w-3.5 ${wsConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
            <span className={wsConnected ? 'text-slate-300' : 'text-slate-500'}>
              {wsConnected ? 'TELEMETRY LIVE' : 'WS OFFLINE'}
            </span>
          </div>

          {/* Operational State Pill */}
          <div className={`px-3 py-1 rounded border text-xs font-mono font-bold tracking-wider shadow-sm flex items-center space-x-1.5 ${getStateBadge(operationalState)}`}>
            <Activity className="h-3.5 w-3.5" />
            <span>STATE: {operationalState}</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin text-amber-400' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
