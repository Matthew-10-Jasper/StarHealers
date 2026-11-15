import React from 'react';
import SeverityBadge from '../common/SeverityBadge';
import {
  Compass,
  Globe,
  Radio,
  Users,
  ShieldAlert,
  Activity,
  HeartPulse,
  History,
  Wind,
  Gauge,
  Thermometer,
  Sun,
  Zap,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  ChevronRight,
} from 'lucide-react';

export default function MissionOverviewView({
  missions,
  selectedMission,
  onSelectMission,
  astronauts,
  onSelectAstronaut,
  onNavigateTab,
  currentUser,
  alerts = [],
  readings = {},
}) {
  const activeAlerts = alerts.filter((a) => a.status === 'ACTIVE');
  const criticalCount = activeAlerts.filter((a) => a.severity === 'CRITICAL').length;
  const warningCount = activeAlerts.filter((a) => a.severity === 'WARNING').length;

  const normalCrewCount = astronauts.filter((a) => a.status === 'NORMAL').length;
  const warningCrewCount = astronauts.filter((a) => a.status === 'WARNING').length;
  const criticalCrewCount = astronauts.filter((a) => a.status === 'CRITICAL').length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-8">
      {/* Welcome Banner / Mission Header */}
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900/90 via-slate-900/80 to-slate-950/90 border border-slate-800 p-6 md:p-8 shadow-xl overflow-hidden backdrop-blur-xl">
        <div className="absolute -right-20 -top-20 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>ACTIVE MISSION CONTROL &bull; FLIGHT MEDICAL STATION</span>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Welcome, <span className="text-cyan-400">{currentUser?.name || 'Dr. Sarah Chen'}</span>
            </h1>

            <p className="text-sm text-slate-300 max-w-2xl">
              Monitoring telemetry for mission <strong className="text-white">{selectedMission.name}</strong> ({selectedMission.target}).
              Trajectory phase: <span className="text-cyan-300 font-mono">{selectedMission.phase}</span>.
            </p>
          </div>

          {/* Mission Switcher & Comms Status */}
          <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end gap-3 shrink-0">
            <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono">
              <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span className="text-slate-400">TELEMETRY LINK:</span>
              <span className="text-emerald-400 font-semibold">SYNCHRONIZED</span>
              <span className="text-slate-500">|</span>
              <span className="text-cyan-400">
                Delay: {selectedMission.commsDelaySec > 60 ? `${Math.round(selectedMission.commsDelaySec / 60)}m` : `${selectedMission.commsDelaySec}s`}
              </span>
            </div>

            {/* Mission Selector Pills */}
            <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono">
              <span className="text-slate-500 px-2 text-[10px] uppercase">Mission:</span>
              {missions.map((m) => (
                <button
                  key={m.id}
                  onClick={() => onSelectMission(m)}
                  className={`px-3 py-1 rounded-lg transition text-xs cursor-pointer ${
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
        </div>
      </div>

      {/* Key Health & Mission Metrics Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Crew Readiness */}
        <div className="glass-card rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Crew Health Index</span>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {criticalCrewCount > 0 ? '78%' : warningCrewCount > 0 ? '92%' : '99%'}
            </span>
            <span className={`text-xs font-semibold ${criticalCrewCount > 0 ? 'text-rose-400' : warningCrewCount > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {criticalCrewCount > 0 ? 'CRITICAL ATTENTION' : warningCrewCount > 0 ? 'STABLE / MONITORED' : 'NOMINAL READINESS'}
            </span>
          </div>
          <div className="mt-3 flex items-center gap-3 text-xs text-slate-400 border-t border-slate-800/80 pt-2.5">
            <span className="text-emerald-400 font-semibold">{normalCrewCount} Optimal</span>
            <span>&bull;</span>
            <span className={warningCrewCount > 0 ? 'text-amber-400 font-semibold' : 'text-slate-500'}>
              {warningCrewCount} Warning
            </span>
            <span>&bull;</span>
            <span className={criticalCrewCount > 0 ? 'text-rose-400 font-semibold' : 'text-slate-500'}>
              {criticalCrewCount} Critical
            </span>
          </div>
        </div>

        {/* Card 2: Active Alerts */}
        <div
          onClick={() => onNavigateTab('triage-alerts')}
          className="glass-card rounded-xl p-5 border border-slate-800 hover:border-amber-500/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Clinical Alerts</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {activeAlerts.length}
            </span>
            <span className="text-xs text-slate-400">active alerts</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs border-t border-slate-800/80 pt-2.5">
            <span className="text-amber-400 font-medium">
              {criticalCount > 0 ? `${criticalCount} Critical, ${warningCount} Warning` : `${warningCount} Warnings`}
            </span>
            <span className="text-cyan-400 flex items-center gap-0.5 text-[11px]">
              Triage <ArrowRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        {/* Card 3: Autonomous Protocol */}
        <div className="glass-card rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Triage Engine</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-400">ACTIVE</span>
            <span className="text-xs text-slate-400">&lt; 250ms latency</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/80 pt-2.5">
            <span>On-board Edge Inference</span>
            <span className="text-emerald-400 font-mono">100% LOC</span>
          </div>
        </div>

        {/* Card 4: Environmental ECLSS */}
        <div className="glass-card rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Habitat ECLSS</span>
            <Wind className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {selectedMission.environment.cabinO2}
            </span>
            <span className="text-xs text-emerald-400 font-medium">O2 Nominal</span>
          </div>
          <div className="mt-3 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/80 pt-2.5">
            <span>CO2: {selectedMission.environment.cabinCo2}</span>
            <span>Temp: {selectedMission.environment.ambientTemp}</span>
          </div>
        </div>
      </div>

      {/* Main Feature Launchpad Shortcuts */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider font-mono">
            Medical Platform Navigation & Core Workspaces
          </h2>
          <span className="text-xs text-slate-400">Select a feature to enter</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Feature 1: Crew Health */}
          <div
            onClick={() => onNavigateTab('vitals-monitoring')}
            className="group relative rounded-xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/50 p-6 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 shadow-lg"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                <Activity className="w-6 h-6" />
              </div>
              <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors">
              Crew Health
            </h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Real-time physiological telemetry monitoring: Heart Rate, HRV, SpO2, Blood Pressure, Hydration, and Sleep.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 text-xs font-medium text-cyan-400">
              <span>Inspect Biometrics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Feature 2: Body Systems */}
          <div
            onClick={() => onNavigateTab('body-map')}
            className="group relative rounded-xl bg-slate-900/80 border border-slate-800 hover:border-sky-500/50 p-6 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 shadow-lg"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-400 group-hover:scale-110 transition-transform">
                <HeartPulse className="w-6 h-6" />
              </div>
              <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-sky-300 transition-colors">
              Body Systems
            </h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Interactive 5-zone holographic anatomical silhouette with zonal telemetry mapping and targeted stress analysis.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 text-xs font-medium text-sky-400">
              <span>View Anatomy Map</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Feature 3: Health Alerts */}
          <div
            onClick={() => onNavigateTab('triage-alerts')}
            className="group relative rounded-xl bg-slate-900/80 border border-slate-800 hover:border-rose-500/50 p-6 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 shadow-lg"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 group-hover:scale-110 transition-transform">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-rose-400 group-hover:translate-x-1 transition-all" />
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-rose-300 transition-colors">
              Health Alerts
            </h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Deterministic clinical triage engine with threshold checking, multi-parameter alerts, and protocol recommendations.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 text-xs font-medium text-rose-400">
              <span>Review Active Alerts ({activeAlerts.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>
      </div>

      {/* Crew Health Quick Status Strip */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800 p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Monitored Crew Roster</h3>
            <span className="text-xs text-slate-400 font-mono">({astronauts.length} Astronauts)</span>
          </div>

          <button
            onClick={() => onNavigateTab('crew-management')}
            className="text-xs font-medium text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
          >
            Open Full Crew Directory <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {astronauts.map((astro) => {
            const astroReadings = readings[astro.id] || {};
            const hr = astroReadings.heartRate?.value || astro.baseline?.restingHr || '--';
            const spo2 = astroReadings.spo2?.value || '--';

            return (
              <div
                key={astro.id}
                onClick={() => {
                  onSelectAstronaut(astro);
                  onNavigateTab('astronaut-dashboard');
                }}
                className="p-3.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition group"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={astro.avatar}
                    alt={astro.name}
                    className="w-10 h-10 rounded-lg object-cover border border-slate-700 shrink-0"
                  />
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-bold text-white truncate group-hover:text-cyan-300 transition-colors">
                      {astro.name}
                    </h4>
                    <span className="text-[10px] text-slate-400 block truncate">
                      {astro.role.split('&')[0]}
                    </span>
                  </div>
                </div>

                <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between">
                  <div className="text-[11px] font-mono text-slate-300">
                    <span className="text-cyan-400 font-bold">{hr}</span> bpm &bull;{' '}
                    <span className="text-blue-400 font-bold">{spo2}%</span> SpO2
                  </div>
                  <SeverityBadge severity={astro.status} size="sm" showIcon={false} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cabin & Environmental Telemetry Matrix */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-mono mb-3 flex items-center gap-2">
          <Wind className="w-4 h-4 text-cyan-400" />
          <span>Spacecraft Habitat & Life Support Telemetry (ECLSS)</span>
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Wind className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[10px] font-mono">CABIN CO2</span>
            </div>
            <div className="text-lg font-bold font-mono text-white">
              {selectedMission.environment.cabinCo2}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Nominal (&lt;0.5%)</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Gauge className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-[10px] font-mono">CABIN O2</span>
            </div>
            <div className="text-lg font-bold font-mono text-white">
              {selectedMission.environment.cabinO2}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Nominal (21%)</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Gauge className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-[10px] font-mono">PRESSURE</span>
            </div>
            <div className="text-lg font-bold font-mono text-white">
              {selectedMission.environment.cabinPressure}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">1.0 Atmosphere</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Thermometer className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[10px] font-mono">AMBIENT TEMP</span>
            </div>
            <div className="text-lg font-bold font-mono text-white">
              {selectedMission.environment.ambientTemp}
            </div>
            <span className="text-[10px] font-mono text-emerald-400">Regulated</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Sun className="w-3.5 h-3.5 text-yellow-400" />
              <span className="text-[10px] font-mono">RADIATION</span>
            </div>
            <div className="text-lg font-bold font-mono text-white">
              {selectedMission.environment.radiationDoseRate}
            </div>
            <span className="text-[10px] font-mono text-amber-400">Active Shield</span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 mb-1">
              <Zap className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[10px] font-mono">GRAVITY</span>
            </div>
            <div className="text-lg font-bold font-mono text-white text-sm">
              {selectedMission.environment.gravity}
            </div>
            <span className="text-[10px] font-mono text-cyan-400">Conditioning</span>
          </div>
        </div>
      </div>
    </div>
  );
}
