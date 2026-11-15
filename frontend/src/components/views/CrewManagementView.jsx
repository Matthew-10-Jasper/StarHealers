import React from 'react';
import SeverityBadge from '../common/SeverityBadge';
import {
  Users,
  User,
  Heart,
  Activity,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export default function CrewManagementView({
  astronauts,
  selectedAstronaut,
  onSelectAstronaut,
  onNavigateTab,
  mission,
  readings = {},
}) {
  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 md:p-8 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
            <Users className="w-3.5 h-3.5 text-cyan-400" />
            <span>MISSION CREW ROSTER &bull; {mission?.name || 'DEEP SPACE EXPEDITION'}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Crew Directory & Health Profiles
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Select any astronaut to inspect their continuous physiological telemetry, interactive 5-zone anatomical model, and active clinical alerts.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className="text-slate-400">MONITORED CREW:</span>{' '}
            <strong className="text-cyan-400 font-bold">{astronauts.length} ASTRONAUTS</strong>
          </div>
        </div>
      </div>

      {/* Grid of Astronaut Profile Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {astronauts.map((astro) => {
          const isSelected = selectedAstronaut.id === astro.id;
          const astroReadings = readings[astro.id] || {};
          const hr = astroReadings.heartRate?.value || astro.baseline?.restingHr || '--';
          const spo2 = astroReadings.spo2?.value || '--';
          const hrv = astroReadings.hrv?.value || '--';
          const stress = astroReadings.stress?.value || '--';

          return (
            <div
              key={astro.id}
              className={`rounded-2xl p-6 border transition-all duration-200 relative flex flex-col justify-between ${
                isSelected
                  ? 'border-cyan-400 bg-slate-900/95 ring-1 ring-cyan-500/40 shadow-xl shadow-cyan-950/30'
                  : 'border-slate-800 bg-slate-900/70 hover:border-slate-700 hover:bg-slate-900/90'
              }`}
            >
              <div>
                {/* Astronaut Identity Row */}
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex items-center gap-3.5">
                    <div className="relative">
                      <img
                        src={astro.avatar}
                        alt={astro.name}
                        className="w-16 h-16 rounded-xl object-cover border-2 border-slate-700"
                      />
                      {isSelected && (
                        <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-4 w-4 bg-cyan-500 text-[9px] font-bold text-slate-950 items-center justify-center">
                            ✓
                          </span>
                        </span>
                      )}
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-lg font-bold text-white tracking-tight">{astro.name}</h2>
                        <span className="text-xs font-mono text-cyan-400 font-semibold px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800/40">
                          {astro.id}
                        </span>
                      </div>
                      <p className="text-xs font-medium text-slate-300 mt-0.5">{astro.role}</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                        Mission: {mission?.name || 'Artemis Deep Space IV'}
                      </p>
                    </div>
                  </div>

                  <SeverityBadge severity={astro.status} size="md" />
                </div>

                {/* Clinical Assessment */}
                <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-300 mb-4">
                  <span className="text-slate-400 font-mono font-semibold uppercase text-[10px] block mb-0.5">
                    Clinical Assessment
                  </span>
                  <span>{astro.statusReason}</span>
                </div>

                {/* Real-time Physiological Telemetry Snapshot */}
                <div className="grid grid-cols-4 gap-2 p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-center mb-4">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">HEART RATE</span>
                    <span className="text-sm font-bold font-mono text-cyan-400">{hr} bpm</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">SPO2</span>
                    <span className="text-sm font-bold font-mono text-blue-400">{spo2}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">HRV</span>
                    <span className="text-sm font-bold font-mono text-purple-400">{hrv} ms</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 block">STRESS</span>
                    <span className="text-sm font-bold font-mono text-amber-400">{stress} pts</span>
                  </div>
                </div>

                {/* Baseline Specs & Blood Type */}
                <div className="grid grid-cols-3 gap-2 px-3 py-2 rounded-lg bg-slate-900/60 border border-slate-800/60 text-xs font-mono text-slate-400 mb-4">
                  <div>
                    <span className="text-[10px] text-slate-500 block">AGE / BLOOD</span>
                    <span className="text-slate-200">{astro.age} yrs &bull; {astro.bloodType}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">HEIGHT / WEIGHT</span>
                    <span className="text-slate-200">{astro.heightCm}cm &bull; {astro.weightKg}kg</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">RESTING BASE</span>
                    <span className="text-cyan-300 font-semibold">{astro.baseline?.restingHr} bpm</span>
                  </div>
                </div>

                {/* Anatomical Status Dots */}
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/80 mb-4">
                  <span>Anatomical Subsystems:</span>
                  <div className="flex items-center gap-2">
                    {Object.entries(astro.bodyRegionStatus || {}).map(([key, st]) => (
                      <span
                        key={key}
                        title={`${key.toUpperCase()}: ${st}`}
                        className={`w-2 h-2 rounded-full ${
                          st === 'CRITICAL'
                            ? 'bg-rose-500 ring-2 ring-rose-500/30'
                            : st === 'WARNING'
                            ? 'bg-amber-400 ring-2 ring-amber-400/30'
                            : st === 'NORMAL'
                            ? 'bg-emerald-400'
                            : 'bg-slate-500'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-3">
                <span className="text-xs font-mono text-slate-400">
                  {isSelected ? 'Active workspace profile' : 'Ready for workspace'}
                </span>

                <button
                  onClick={() => {
                    onSelectAstronaut(astro);
                    onNavigateTab('astronaut-dashboard');
                  }}
                  className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 shadow-lg shadow-cyan-500/20 hover:from-cyan-400 hover:to-blue-500'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white'
                  }`}
                >
                  <span>{isSelected ? 'Open Health Workspace' : 'Select Astronaut'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
