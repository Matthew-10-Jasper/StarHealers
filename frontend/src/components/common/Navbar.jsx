import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Radio, User, Clock, Globe, LogOut } from 'lucide-react';
import SeverityBadge from './SeverityBadge';

export default function Navbar({
  missions,
  selectedMission,
  onSelectMission,
  astronauts,
  selectedAstronaut,
  onSelectAstronaut,
  isLiveSimulating,
  onToggleLiveSimulating,
  activeAlertsCount,
  currentUser,
  onSignOut,
}) {
  const [currentTime, setCurrentTime] = useState(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toUTCString().replace('GMT', 'UTC'));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-6 py-2.5">
      <div className="flex items-center justify-between gap-4">
        {/* Left: StarHealers Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/40 shadow-cyan-glow">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-wider text-slate-100 font-sans">
                STAR<span className="text-cyan-400">HEALERS</span>
              </span>
            </div>
            <p className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
              Aerospace Medical Platform
            </p>
          </div>
        </div>

        {/* Center: Mission Selector & Astronaut Selector Controls */}
        <div className="hidden md:flex items-center gap-3">
          {/* Mission Dropdown */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <Globe className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-400 font-mono">MISSION:</span>
            <select
              value={selectedMission.id}
              onChange={(e) => {
                const m = missions.find((item) => item.id === e.target.value);
                if (m) onSelectMission(m);
              }}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer pr-1"
            >
              {missions.map((m) => (
                <option key={m.id} value={m.id} className="bg-slate-900 text-slate-200">
                  {m.name} ({m.target})
                </option>
              ))}
            </select>
            <span className="text-[10px] font-mono text-cyan-400/80 pl-1 border-l border-slate-800">
              Delay: {selectedMission.commsDelaySec > 60 ? `${Math.round(selectedMission.commsDelaySec / 60)}m` : `${selectedMission.commsDelaySec}s`}
            </span>
          </div>

          {/* Astronaut Selector */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
            <User className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400 font-mono">CREW:</span>
            <select
              value={selectedAstronaut.id}
              onChange={(e) => {
                const a = astronauts.find((item) => item.id === e.target.value);
                if (a) onSelectAstronaut(a);
              }}
              className="bg-transparent text-slate-100 font-semibold focus:outline-none cursor-pointer pr-1"
            >
              {astronauts.map((a) => (
                <option key={a.id} value={a.id} className="bg-slate-900 text-slate-200">
                  {a.name} ({a.role.split('&')[0].trim()})
                </option>
              ))}
            </select>
            <SeverityBadge severity={selectedAstronaut.status} size="sm" showIcon={false} />
          </div>
        </div>

        {/* Right: Live Stream Toggle, Clock & Medical Officer Session */}
        <div className="flex items-center gap-3">
          {/* Live Simulator Status Toggle */}
          <button
            onClick={onToggleLiveSimulating}
            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg border text-xs font-mono transition cursor-pointer ${
              isLiveSimulating
                ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-300'
                : 'bg-slate-900/80 border-slate-800 text-slate-400'
            }`}
            title="Toggle autonomous telemetry streaming"
          >
            <Radio className={`w-3.5 h-3.5 ${isLiveSimulating ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
            <span className="hidden sm:inline">
              {isLiveSimulating ? 'TELEMETRY: STREAMING' : 'TELEMETRY: PAUSED'}
            </span>
          </button>

          {/* UTC Clock */}
          <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/50 border border-slate-800/80 text-[11px] font-mono text-slate-400">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>{currentTime.split(' ').slice(4, 5)[0]} UTC</span>
          </div>

          {/* Active Alerts Pill */}
          {activeAlertsCount > 0 && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-950/60 border border-rose-500/40 text-rose-300 text-xs font-mono">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-400 animate-bounce" />
              <span>{activeAlertsCount} ALERT{activeAlertsCount > 1 ? 'S' : ''}</span>
            </div>
          )}

          {/* Medical Officer Profile Indicator */}
          <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-cyan-900/60 border border-cyan-500/40 flex items-center justify-center text-cyan-300 font-bold text-xs">
              {currentUser?.name ? currentUser.name[0] : 'M'}
            </div>
            <div className="hidden lg:block text-left">
              <p className="text-xs font-medium text-slate-200">
                {currentUser?.name || 'Dr. Sarah Chen'}
              </p>
              <p className="text-[10px] font-mono text-slate-400">
                {currentUser?.role || 'Flight Surgeon'}
              </p>
            </div>
            {onSignOut && (
              <button
                onClick={onSignOut}
                title="Sign Out"
                className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800/60 transition ml-1"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
