import React, { useEffect, useState } from 'react';
import {
  Shield,
  Radio,
  Activity,
  AlertTriangle,
  RefreshCw,
  Cpu,
  Brain,
  Sun,
  Flame,
  Heart,
  Database,
  Layers,
  User,
  ChevronDown,
} from 'lucide-react';
import { OperationalState, QualityStatus } from '../types/mission';
import { ActiveModuleId, useSharedMission } from '../context/SharedMissionContext';

interface HeaderProps {
  operationalState: OperationalState;
  missionName: string;
  contextVersion: number;
  dataQuality: QualityStatus;
  wsConnected: boolean;
  onRefresh: () => void;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  operationalState,
  missionName,
  contextVersion,
  dataQuality,
  wsConnected,
  onRefresh,
  isLoading,
}) => {
  const {
    activeModule,
    setActiveModule,
    astronauts,
    selectedAstronautId,
    setSelectedAstronautId,
  } = useSharedMission();

  const [elapsedTime, setElapsedTime] = useState('00d 00h 00m 00s');
  const [isAstroDropdownOpen, setIsAstroDropdownOpen] = useState(false);

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
        return 'bg-crimson-950/80 text-rose-400 border-rose-500 shadow-rose-900/40 animate-pulse';
      case 'RECOVERY':
        return 'bg-cyan-950/60 text-cyan-400 border-cyan-500/60 shadow-cyan-900/30';
      case 'UNKNOWN':
      default:
        return 'bg-slate-900 text-slate-300 border-slate-600 shadow-slate-900/20';
    }
  };

  const navItems: { id: ActiveModuleId; label: string; icon: any; accent: string }[] = [
    { id: 'OVERVIEW', label: 'OVERVIEW', icon: Layers, accent: 'text-cyan-400 border-cyan-500/50 bg-cyan-500/10' },
    { id: 'MODULE_1', label: 'M1: VITALS', icon: Heart, accent: 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10' },
    { id: 'MODULE_2', label: 'M2: BODY MAP', icon: Activity, accent: 'text-purple-400 border-purple-500/50 bg-purple-500/10' },
    { id: 'MODULE_3', label: 'M3: TRIAGE', icon: Shield, accent: 'text-rose-400 border-rose-500/50 bg-rose-500/10' },
    { id: 'MODULE_4', label: 'M4: MISSION', icon: Cpu, accent: 'text-red-400 border-red-500/50 bg-red-500/10' },
    { id: 'MODULE_5', label: 'M5: HAZARDS', icon: Flame, accent: 'text-amber-400 border-amber-500/50 bg-amber-500/10' },
    { id: 'MODULE_6', label: 'M6: CIRCADIAN', icon: Brain, accent: 'text-indigo-400 border-indigo-500/50 bg-indigo-500/10' },
    { id: 'MODULE_7', label: 'M7: SPACE ENV', icon: Sun, accent: 'text-yellow-400 border-yellow-500/50 bg-yellow-500/10' },
    { id: 'SYSTEM_HEALTH', label: 'HEALTH', icon: Database, accent: 'text-teal-400 border-teal-500/50 bg-teal-500/10' },
  ];

  const currentAstronaut = astronauts.find((a) => a.id === selectedAstronautId) || astronauts[0];

  return (
    <header className="border-b border-[#1E293B] bg-[#0F172A]/90 backdrop-blur-md px-4 sm:px-6 py-3 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex flex-col gap-3">
        {/* Top Tier: Branding, Astronaut Selector, State & Connectivity */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500/30 via-cyan-500/30 to-amber-500/30 border border-slate-700 flex items-center justify-center">
              <Activity className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-mono text-[11px] tracking-widest text-[#38BDF8] uppercase font-bold">
                  STARHEALERS • UNIFIED PLATFORM
                </span>
                <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-300 px-1.5 py-0.2 rounded font-mono">
                  v1.0.0
                </span>
              </div>
              <h1 className="text-sm sm:text-base font-bold text-[#F8FAFC] tracking-tight">
                Astronaut Health & Spaceflight Monitoring Subsystem
              </h1>
            </div>
          </div>

          {/* Right Status Controls */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Astronaut Quick Selector */}
            <div className="relative">
              <button
                onClick={() => setIsAstroDropdownOpen(!isAstroDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-[#060913] border border-[#1E293B] hover:border-slate-700 text-xs font-mono text-slate-200 transition"
              >
                <User className="w-3.5 h-3.5 text-cyan-400" />
                <span className="font-bold">{currentAstronaut?.name || selectedAstronautId}</span>
                <span className="text-[10px] text-slate-500">({selectedAstronautId})</span>
                <ChevronDown className="w-3 h-3 text-slate-500" />
              </button>

              {isAstroDropdownOpen && (
                <div className="absolute right-0 mt-1 w-56 rounded-xl bg-[#0F172A] border border-slate-700 shadow-xl py-1 z-50">
                  <div className="px-3 py-1.5 text-[10px] font-mono text-slate-400 border-b border-slate-800">
                    SELECT ACTIVE CREW MEMBER
                  </div>
                  {astronauts.map((a) => (
                    <button
                      key={a.id}
                      onClick={() => {
                        setSelectedAstronautId(a.id);
                        setIsAstroDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-xs font-mono flex items-center justify-between hover:bg-slate-800/80 transition ${
                        a.id === selectedAstronautId ? 'text-cyan-400 font-bold bg-cyan-950/30' : 'text-slate-300'
                      }`}
                    >
                      <span>{a.name}</span>
                      <span className="text-[10px] text-slate-500">{a.id}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* WebSocket / Telemetry Live */}
            <div className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-[#060913] border border-[#1E293B] text-xs font-mono">
              <Radio className={`h-3.5 w-3.5 ${wsConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
              <span className={wsConnected ? 'text-slate-300' : 'text-slate-500'}>
                {wsConnected ? 'LIVE' : 'OFFLINE'}
              </span>
            </div>

            {/* Operational State */}
            <div className={`px-3 py-1 rounded-lg border text-xs font-mono font-bold tracking-wider shadow-sm flex items-center space-x-1.5 ${getStateBadge(operationalState)}`}>
              <Activity className="h-3.5 w-3.5" />
              <span>{operationalState}</span>
            </div>

            {/* Global Refresh */}
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Lower Tier: Module Navigation Tabs Bar */}
        <nav className="flex items-center space-x-1 overflow-x-auto pb-0.5 scrollbar-thin">
          {navItems.map((item) => {
            const isActive = activeModule === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveModule(item.id)}
                className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all flex items-center space-x-1.5 shrink-0 ${
                  isActive
                    ? `${item.accent} border shadow-sm`
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                {React.createElement(item.icon, { className: 'h-3.5 w-3.5' })}
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
