import React, { useState, useEffect } from 'react';
import { useSharedMission, ActiveModuleId } from '../../context/SharedMissionContext';
import { apiClient } from '../../services/apiClient';
import {
  Activity,
  Shield,
  Radio,
  Flame,
  Brain,
  Sun,
  Database,
  ArrowRight,
  Heart,
  Moon,
  Radiation,
  Wind,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  RefreshCw,
} from 'lucide-react';

export const UnifiedMissionOverview: React.FC = () => {
  const {
    astronauts,
    selectedAstronautId,
    setSelectedAstronautId,
    setActiveModule,
    systemHealth,
  } = useSharedMission();

  const [overviewData, setOverviewData] = useState<any>(null);
  const [missionContext, setMissionContext] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [spaceEnv, setSpaceEnv] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchOverview = async () => {
    try {
      setIsLoading(true);
      const [ov, ctx, alts, env] = await Promise.allSettled([
        apiClient.getUnifiedOverview(),
        apiClient.getCurrentMissionContext(),
        apiClient.getAlerts(),
        apiClient.getSpaceEnvironmentTelemetry(),
      ]);

      if (ov.status === 'fulfilled') setOverviewData(ov.value);
      if (ctx.status === 'fulfilled') setMissionContext(ctx.value);
      if (alts.status === 'fulfilled' && Array.isArray(alts.value)) setAlerts(alts.value);
      if (env.status === 'fulfilled') setSpaceEnv(env.value);
    } catch (e) {
      console.warn('[UnifiedMissionOverview] Fetch error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const opState = missionContext?.operational_state || 'NOMINAL';
  const activeDeviations = missionContext?.active_deviations?.length || 0;
  const criticalAlerts = alerts.filter((a) => a.severity === 'CRITICAL' && a.status === 'ACTIVE').length;

  const getStateStyle = (state: string) => {
    switch (state) {
      case 'NOMINAL':
        return 'text-emerald-400 bg-emerald-950/60 border-emerald-500/50';
      case 'DEGRADED':
        return 'text-amber-400 bg-amber-950/60 border-amber-500/50';
      case 'CONTINGENCY':
        return 'text-rose-400 bg-rose-950/80 border-rose-500 animate-pulse';
      case 'RECOVERY':
        return 'text-cyan-400 bg-cyan-950/60 border-cyan-500/50';
      default:
        return 'text-slate-400 bg-slate-900 border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Mission Status Banner */}
      <div className="bg-[#0F172A]/90 border border-[#1E293B] rounded-2xl p-6 backdrop-blur-md relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <span className="font-mono text-xs text-cyan-400 tracking-wider font-semibold uppercase">
                STARHEALERS CONSOLIDATED COMMAND CENTER
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                7 MODULES INTEGRATED
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F8FAFC] tracking-tight">
              Mission Operations & Integrated Astronaut Health Portal
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 max-w-3xl leading-relaxed">
              Consolidated aerospace telemetry synthesizing continuous biometrics, anatomical strain, autonomous triage protocols, mission context adaptations, physics simulation engines, and circadian cognitive readiness.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <div className={`px-4 py-2 rounded-xl border font-mono text-xs font-bold shadow-sm flex items-center space-x-2 ${getStateStyle(opState)}`}>
              <Activity className="w-4 h-4" />
              <span>STATE: {opState}</span>
            </div>

            <button
              onClick={fetchOverview}
              disabled={isLoading}
              className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition"
              title="Refresh Platform State"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* High-Level KPI Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-[#1E293B]">
          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-800/80">
            <div className="text-[11px] font-mono text-slate-400">ACTIVE CREW</div>
            <div className="text-xl font-bold font-mono text-white mt-1">4 ASTRONAUTS</div>
            <div className="text-[10px] text-emerald-400 font-mono mt-0.5">3 Nominal • 1 Observed</div>
          </div>
          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-800/80">
            <div className="text-[11px] font-mono text-slate-400">ACTIVE DEVIATIONS</div>
            <div className={`text-xl font-bold font-mono mt-1 ${activeDeviations > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {activeDeviations} DEVIATIONS
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">M4 Flight Context</div>
          </div>
          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-800/80">
            <div className="text-[11px] font-mono text-slate-400">CLINICAL TRIAGE ALERTS</div>
            <div className={`text-xl font-bold font-mono mt-1 ${criticalAlerts > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {alerts.length} ALERTS ({criticalAlerts} CRIT)
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">M3 Protocol Advisor</div>
          </div>
          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-800/80">
            <div className="text-[11px] font-mono text-slate-400">SYSTEM HEALTH</div>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">OPERATIONAL</div>
            <div className="text-[10px] text-slate-400 font-mono mt-0.5">5/5 DBs Connected</div>
          </div>
        </div>
      </div>

      {/* Astronaut Crew Health Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold font-mono text-slate-300 tracking-wider uppercase flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span>CREW MONITORING FLEET</span>
          </h2>
          <span className="text-xs text-slate-500 font-mono">Click card to inspect astronaut vitals</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {astronauts.map((astro) => {
            const isSelected = astro.id === selectedAstronautId;
            const status = astro.id === 'ASTRO-01' ? 'WARNING' : 'NORMAL';
            const hr = astro.id === 'ASTRO-01' ? '112 BPM' : '68 BPM';
            const sleepDebt = astro.id === 'ASTRO-01' ? '3.8 hrs' : '0.8 hrs';
            const dose = astro.id === 'ASTRO-01' ? '18.4 mSv' : '12.2 mSv';

            return (
              <div
                key={astro.id}
                onClick={() => {
                  setSelectedAstronautId(astro.id);
                  setActiveModule('MODULE_1');
                }}
                className={`p-4 rounded-xl border cursor-pointer transition-all relative ${
                  isSelected
                    ? 'bg-slate-800/90 border-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                    : 'bg-[#0F172A]/70 hover:bg-[#0F172A] border-[#1E293B] hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <img
                      src={astro.avatar}
                      alt={astro.name}
                      className="w-10 h-10 rounded-full object-cover border border-slate-700"
                    />
                    <div>
                      <div className="text-xs font-mono font-bold text-slate-400">[{astro.id}]</div>
                      <div className="text-sm font-bold text-white line-clamp-1">{astro.name}</div>
                    </div>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                    status === 'WARNING' ? 'text-amber-400 bg-amber-950/60 border-amber-500/50' : 'text-emerald-400 bg-emerald-950/60 border-emerald-500/50'
                  }`}>
                    {status}
                  </span>
                </div>

                <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-3 gap-2 text-center font-mono">
                  <div>
                    <div className="text-[10px] text-slate-500">HEART</div>
                    <div className="text-xs font-bold text-white mt-0.5">{hr}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500">SLEEP DEBT</div>
                    <div className="text-xs font-bold text-white mt-0.5">{sleepDebt}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500">RAD DOSE</div>
                    <div className="text-xs font-bold text-white mt-0.5">{dose}</div>
                  </div>
                </div>

                <div className="mt-3 flex items-center justify-between text-[11px] text-cyan-400 font-mono font-medium">
                  <span>View Telemetry</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Module Navigation Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold font-mono text-slate-300 tracking-wider uppercase flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <span>MISSION SUBSYSTEMS & MODULE HUBS</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            {
              id: 'MODULE_1' as ActiveModuleId,
              title: 'Module 1 • Continuous Vitals & Biometrics',
              desc: 'High-frequency physiological telemetry: ECG, HRV, SpO2, glucose, thermal balance.',
              accent: 'border-emerald-500/40 hover:border-emerald-400',
              icon: Heart,
              iconColor: 'text-emerald-400',
              badge: 'SUBA ENGINE',
            },
            {
              id: 'MODULE_2' as ActiveModuleId,
              title: 'Module 2 • Interactive Body Anatomy Map',
              desc: '2D/3D organ systems projection with microgravity stress & clinical observations.',
              accent: 'border-purple-500/40 hover:border-purple-400',
              icon: Activity,
              iconColor: 'text-purple-400',
              badge: 'ORGAN TELEMETRY',
            },
            {
              id: 'MODULE_3' as ActiveModuleId,
              title: 'Module 3 • Autonomous Medical Triage',
              desc: 'Automated flight-rule evaluation and clinical protocol guidance (NASA-STD-3001).',
              accent: 'border-rose-500/40 hover:border-rose-400',
              icon: Shield,
              iconColor: 'text-rose-400',
              badge: 'CLINICAL ADVISOR',
            },
            {
              id: 'MODULE_4' as ActiveModuleId,
              title: 'Module 4 • Mission Intelligence & Adaptive Context',
              desc: 'Environmental differential matrix, operational states, active flight deviations.',
              accent: 'border-red-500/40 hover:border-red-400',
              icon: Cpu,
              iconColor: 'text-red-400',
              badge: 'MISSION CONTEXT',
            },
            {
              id: 'MODULE_5' as ActiveModuleId,
              title: 'Module 5 • Space Hazard Simulation Engine',
              desc: 'Authoritative physical solver for Space Radiation, Cabin CO2, and sleep deficit ODEs.',
              accent: 'border-amber-500/40 hover:border-amber-400',
              icon: Flame,
              iconColor: 'text-amber-400',
              badge: 'PHYSICS SIMULATOR',
            },
            {
              id: 'MODULE_6' as ActiveModuleId,
              title: 'Module 6 • Circadian Rhythm & Psychomotor Fatigue',
              desc: '3-process sleep-wake model, PVT neurobehavioral reaction time test battery.',
              accent: 'border-indigo-500/40 hover:border-indigo-400',
              icon: Brain,
              iconColor: 'text-indigo-400',
              badge: 'COGNITIVE READINESS',
            },
            {
              id: 'MODULE_7' as ActiveModuleId,
              title: 'Module 7 • Space Weather & Radiation Limits',
              desc: 'Solar particle events, galactic cosmic rays, ECLSS life support telemetry.',
              accent: 'border-yellow-500/40 hover:border-yellow-400',
              icon: Sun,
              iconColor: 'text-yellow-400',
              badge: 'SPACE WEATHER',
            },
            {
              id: 'SYSTEM_HEALTH' as ActiveModuleId,
              title: 'System Health & Persistence Monitor',
              desc: 'Audit connectivity to all 5 SQLite databases and 7 internal module microservices.',
              accent: 'border-cyan-500/40 hover:border-cyan-400',
              icon: Database,
              iconColor: 'text-cyan-400',
              badge: 'DIAGNOSTICS',
            },
          ].map((m) => (
            <div
              key={m.id}
              onClick={() => setActiveModule(m.id)}
              className={`p-5 rounded-xl bg-[#0F172A]/70 hover:bg-[#0F172A] border ${m.accent} cursor-pointer transition-all duration-200 group flex flex-col justify-between`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                    {React.createElement(m.icon, { className: `w-5 h-5 ${m.iconColor}` })}
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                    {m.badge}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                  {m.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {m.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-400 group-hover:text-white transition-colors">
                <span>OPEN DASHBOARD</span>
                <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
