import React from 'react';
import SeverityBadge from '../common/SeverityBadge';
import { Users, User, Heart, Activity, ArrowRight, ShieldCheck } from 'lucide-react';

export default function CrewManagementView({
  astronauts,
  selectedAstronaut,
  onSelectAstronaut,
  onNavigateTab,
}) {
  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-white font-sans tracking-wide">
              Crew Management & Physiological Profiles
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
              Active Crew: {astronauts.length}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Fictional prototype astronaut profiles with validated baseline physiology and individual sensor identifiers.
          </p>
        </div>
      </div>

      {/* Grid of Astronaut Profiles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {astronauts.map((astro) => {
          const isSelected = selectedAstronaut.id === astro.id;

          return (
            <div
              key={astro.id}
              className={`glass-panel rounded-xl p-5 border transition relative ${
                isSelected
                  ? 'border-cyan-400 ring-1 ring-cyan-400/50 shadow-cyan-glow bg-slate-900/90'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <img
                    src={astro.avatar}
                    alt={astro.name}
                    className="w-14 h-14 rounded-xl object-cover border-2 border-slate-700"
                  />
                  <div>
                    <h3 className="text-base font-bold text-white font-sans">{astro.name}</h3>
                    <span className="text-xs font-mono text-cyan-400 font-semibold">{astro.id}</span>
                    <p className="text-xs text-slate-400">{astro.role}</p>
                  </div>
                </div>

                <SeverityBadge severity={astro.status} size="md" />
              </div>

              {/* Status Reason */}
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300 mb-4">
                <strong className="text-slate-400 font-mono">ASSESSMENT:</strong> {astro.statusReason}
              </div>

              {/* Bio & Baseline Specs */}
              <div className="grid grid-cols-3 gap-2 p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono mb-4">
                <div>
                  <span className="text-[10px] text-slate-400 block">AGE / BLOOD</span>
                  <span className="text-white">{astro.age} yrs • {astro.bloodType}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">HEIGHT / WEIGHT</span>
                  <span className="text-white">{astro.heightCm}cm • {astro.weightKg}kg</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">RESTING HR BASE</span>
                  <span className="text-cyan-400 font-bold">{astro.baseline.restingHr} bpm</span>
                </div>
              </div>

              {/* System status dots */}
              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-3 border-t border-slate-800">
                <span>Anatomical Status:</span>
                <div className="flex items-center gap-2">
                  {Object.entries(astro.bodyRegionStatus || {}).map(([key, st]) => (
                    <span
                      key={key}
                      title={`${key}: ${st}`}
                      className={`w-2 h-2 rounded-full ${
                        st === 'CRITICAL'
                          ? 'bg-rose-500'
                          : st === 'WARNING'
                          ? 'bg-amber-400'
                          : st === 'NORMAL'
                          ? 'bg-emerald-400'
                          : 'bg-slate-500'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Select Crew CTA Button */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">
                  {isSelected ? '✓ Currently Selected' : 'Ready for Cockpit'}
                </span>
                <button
                  onClick={() => {
                    onSelectAstronaut(astro);
                    onNavigateTab('astronaut-dashboard');
                  }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition ${
                    isSelected
                      ? 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-cyan-glow'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
                  }`}
                >
                  <span>Select & Inspect</span>
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
