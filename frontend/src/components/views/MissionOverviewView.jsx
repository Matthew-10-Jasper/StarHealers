import React from 'react';
import SeverityBadge from '../common/SeverityBadge';
import {
  Compass,
  Globe,
  Radio,
  Users,
  Shield,
  Zap,
  Thermometer,
  Wind,
  Gauge,
  Sun,
  ArrowRight,
} from 'lucide-react';

export default function MissionOverviewView({
  missions,
  selectedMission,
  onSelectMission,
  astronauts,
  onSelectAstronaut,
  onNavigateTab,
}) {
  return (
    <div className="space-y-6">
      {/* Mission Header */}
      <div className="glass-panel rounded-xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Globe className="w-5 h-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white font-sans tracking-wide">
              {selectedMission.name}
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/40">
              {selectedMission.target.toUpperCase()}
            </span>
          </div>
          <p className="text-xs text-slate-300 font-mono">
            {selectedMission.phase} • Comms Delay: <strong className="text-cyan-400">{selectedMission.commsDelaySec > 60 ? `${Math.round(selectedMission.commsDelaySec / 60)} minutes` : `${selectedMission.commsDelaySec} seconds`}</strong> to Earth Ground Control
          </p>
        </div>

        {/* Mission Switcher Buttons */}
        <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
          {missions.map((m) => (
            <button
              key={m.id}
              onClick={() => onSelectMission(m)}
              className={`px-3 py-1.5 rounded transition ${
                selectedMission.id === m.id
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {m.target}
            </button>
          ))}
        </div>
      </div>

      {/* Autonomous Operational Paradigm Notice */}
      <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-800/40 text-xs text-slate-300 flex items-start gap-3">
        <Radio className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-cyan-300 font-semibold font-mono mb-1">
            AUTONOMOUS LOCAL MEDICAL OPERATION REQUIRED
          </h4>
          <p className="leading-relaxed">
            Due to the {selectedMission.commsDelaySec > 60 ? `${Math.round(selectedMission.commsDelaySec / 60)}-minute` : `${selectedMission.commsDelaySec}-second`} one-way round-trip communication delay to Earth, real-time telemetry cannot rely on Mission Control flight surgeons. StarHealers executes local physiological rule evaluation, compound anomaly detection, and autonomous escalation guidance directly on the spacecraft edge node.
          </p>
        </div>
      </div>

      {/* Cabin & Environmental Telemetry Matrix */}
      <div>
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Wind className="w-4 h-4 text-cyan-400" />
          <span>Spacecraft Habitat & Life Support Telemetry (ECLSS)</span>
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Wind className="w-4 h-4 text-cyan-400" />
              <span className="text-[10px] font-mono">CABIN CO2</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {selectedMission.environment.cabinCo2}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Nominal (&lt;0.5%)</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Gauge className="w-4 h-4 text-blue-400" />
              <span className="text-[10px] font-mono">CABIN O2</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {selectedMission.environment.cabinO2}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Nominal (21%)</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Gauge className="w-4 h-4 text-purple-400" />
              <span className="text-[10px] font-mono">PRESSURE</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {selectedMission.environment.cabinPressure}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">1.0 Atmosphere</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Thermometer className="w-4 h-4 text-amber-400" />
              <span className="text-[10px] font-mono">AMBIENT TEMP</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {selectedMission.environment.ambientTemp}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Regulated</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Sun className="w-4 h-4 text-yellow-400" />
              <span className="text-[10px] font-mono">RADIATION DOSE</span>
            </div>
            <div className="text-xl font-bold font-mono text-white">
              {selectedMission.environment.radiationDoseRate}
            </div>
            <span className="text-[10px] font-mono text-amber-400">Active GCR/SPE</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Zap className="w-4 h-4 text-emerald-400" />
              <span className="text-[10px] font-mono">GRAVITY ENV</span>
            </div>
            <div className="text-xl font-bold font-mono text-white text-sm">
              {selectedMission.environment.gravity}
            </div>
            <span className="text-[10px] font-mono text-cyan-400">Conditioning Active</span>
          </div>
        </div>
      </div>

      {/* Crew Health Status Roster */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-400" />
            <span>Assigned Mission Crew ({astronauts.length} Astronauts)</span>
          </h3>
          <button
            onClick={() => onNavigateTab('crew-management')}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            Crew Management <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {astronauts.map((astro) => (
            <div
              key={astro.id}
              onClick={() => {
                onSelectAstronaut(astro);
                onNavigateTab('astronaut-dashboard');
              }}
              className="glass-card rounded-xl p-4 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition space-y-3"
            >
              <div className="flex items-center gap-3">
                <img
                  src={astro.avatar}
                  alt={astro.name}
                  className="w-11 h-11 rounded-lg object-cover border border-slate-700"
                />
                <div>
                  <h4 className="text-xs font-bold text-white font-sans">{astro.name}</h4>
                  <span className="text-[10px] font-mono text-cyan-400 block">{astro.id}</span>
                  <span className="text-[10px] text-slate-400 truncate block max-w-[130px]">
                    {astro.role.split('&')[0]}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                <SeverityBadge severity={astro.status} size="sm" />
                <span className="text-[10px] font-mono text-slate-400 group-hover:text-cyan-300">
                  Select →
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
