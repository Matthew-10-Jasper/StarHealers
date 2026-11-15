import React, { useState, useEffect, useCallback } from 'react';
import {
  apiM6,
  Astronaut,
  SleepStatus,
  CircadianRhythm,
  FatigueAssessment,
  StressMonitoring,
  CognitiveReadiness,
  PVTHistory,
  PVTSession
} from '../../services/modulesApi';
import { PVTTestInterface } from './PVTTestInterface';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid
} from 'recharts';
import {
  User, Moon, Sun, Activity, Brain, ShieldAlert,
  Info, Clock, RefreshCw, HeartPulse, ChevronRight
} from 'lucide-react';

export const Module6Dashboard: React.FC = () => {
  const [astronauts, setAstronauts] = useState<Astronaut[]>([]);
  const [selectedAstronautId, setSelectedAstronautId] = useState<string>('ASTRO-01');
  const [sleep, setSleep] = useState<SleepStatus | null>(null);
  const [circadian, setCircadian] = useState<CircadianRhythm | null>(null);
  const [fatigue, setFatigue] = useState<FatigueAssessment | null>(null);
  const [stress, setStress] = useState<StressMonitoring | null>(null);
  const [readiness, setReadiness] = useState<CognitiveReadiness | null>(null);
  const [pvtHistory, setPvtHistory] = useState<PVTHistory | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadAstronautData = useCallback(async (astroId: string) => {
    try {
      setIsRefreshing(true);
      const [sData, cData, fData, stData, rData, pvtData] = await Promise.all([
        apiM6.getSleep(astroId),
        apiM6.getCircadian(astroId),
        apiM6.getFatigue(astroId),
        apiM6.getStress(astroId),
        apiM6.getReadiness(astroId),
        apiM6.getPVTHistory(astroId)
      ]);
      setSleep(sData);
      setCircadian(cData);
      setFatigue(fData);
      setStress(stData);
      setReadiness(rData);
      setPvtHistory(pvtData);
    } catch (err) {
      console.error('Failed to load astronaut data:', err);
    } finally {
      setIsRefreshing(false);
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      try {
        const astros = await apiM6.getAstronauts();
        setAstronauts(astros);
        if (astros.length > 0) {
          const initialId = astros[0].astronaut_id;
          setSelectedAstronautId(initialId);
          await loadAstronautData(initialId);
        }
      } catch (err) {
        console.error('Failed to init Module 6:', err);
        // Fallback default list
        const fallback = [
          { astronaut_id: 'ASTRO-01', name: 'Cmdr. Sarah Vance', role: 'Mission Commander', baseline_sleep_hours: 8, baseline_hrv_rmssd: 55 },
          { astronaut_id: 'ASTRO-02', name: 'Maj. Mark Robinson', role: 'Command Module Pilot', baseline_sleep_hours: 7.5, baseline_hrv_rmssd: 50 },
          { astronaut_id: 'ASTRO-03', name: 'Dr. Elena Rostova', role: 'Chief Science Officer', baseline_sleep_hours: 8, baseline_hrv_rmssd: 52 },
          { astronaut_id: 'ASTRO-04', name: 'Lt. Chen Wei', role: 'Flight Engineer', baseline_sleep_hours: 8, baseline_hrv_rmssd: 48 }
        ];
        setAstronauts(fallback);
        setSelectedAstronautId('ASTRO-01');
        await loadAstronautData('ASTRO-01');
      }
    };
    init();
  }, [loadAstronautData]);

  const handleSelectAstronaut = (id: string) => {
    setSelectedAstronautId(id);
    loadAstronautData(id);
  };

  const handleSessionComplete = (session: PVTSession) => {
    // Refresh readiness and pvt history
    loadAstronautData(selectedAstronautId);
  };

  const currentAstronaut = astronauts.find(a => a.astronaut_id === selectedAstronautId);

  return (
    <div className="space-y-6">
      {/* Subsystem Header */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-[#6366F1]/30 text-[#6366F1]">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#6366F1]/20 text-[#38BDF8] border border-[#6366F1]/30 font-bold uppercase tracking-wider">
                  MODULE 6
                </span>
                <span className="text-xs font-mono text-slate-400">PORT 8006</span>
              </div>
              <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
                Circadian Rhythm, Fatigue & Psychomotor Stress Subsystem
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => loadAstronautData(selectedAstronautId)}
              disabled={isRefreshing}
              className="px-3 py-1.5 rounded-lg bg-[#1E293B] hover:bg-slate-800 text-slate-300 font-mono text-xs flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-[#38BDF8]' : ''}`} />
              <span>Sync Biomarkers</span>
            </button>
          </div>
        </div>

        {/* Astronaut Selector Pills */}
        <div className="mt-5 pt-4 border-t border-[#1E293B] flex items-center space-x-2 overflow-x-auto pb-1">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider mr-2 shrink-0 flex items-center">
            <User className="h-3.5 w-3.5 mr-1 text-[#38BDF8]" /> Active Crew:
          </span>
          {astronauts.map(a => {
            const isSelected = a.astronaut_id === selectedAstronautId;
            return (
              <button
                key={a.astronaut_id}
                onClick={() => handleSelectAstronaut(a.astronaut_id)}
                className={`px-3.5 py-1.5 rounded-lg font-mono text-xs font-medium transition-all shrink-0 flex items-center space-x-2 border ${isSelected
                    ? 'bg-[#6366F1]/20 border-[#6366F1] text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]'
                    : 'bg-[#060913] border-[#1E293B] text-slate-400 hover:text-slate-200 hover:border-slate-700'
                  }`}
              >
                <span className="font-bold">{a.astronaut_id}</span>
                <span className="text-slate-400 hidden sm:inline">| {a.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Non-Clinical Decision Support Disclaimer */}
      {readiness && (
        <div className="p-3.5 rounded-xl bg-indigo-950/40 border border-[#6366F1]/30 flex items-start space-x-3 text-indigo-200 text-xs">
          <Info className="h-4 w-4 text-[#38BDF8] shrink-0 mt-0.5" />
          <p className="font-mono leading-relaxed">
            <strong className="text-white">NOTICE: </strong>
            {readiness.non_clinical_disclaimer}
          </p>
        </div>
      )}

      {/* Section 1: Cognitive Readiness Multi-Factor Hero */}
      {readiness && (
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 shadow-xl">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="flex items-center space-x-5">
              <div className="relative flex items-center justify-center">
                <div className={`w-28 h-28 rounded-full flex flex-col items-center justify-center border-4 shadow-2xl ${readiness.rating === 'OPTIMAL_PERFORMANCE'
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                    : readiness.rating === 'QUALIFIED_MONITORED'
                      ? 'border-sky-500 bg-sky-500/10 text-sky-400'
                      : readiness.rating === 'DEGRADED_RESTRICTED'
                        ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                        : 'border-rose-500 bg-rose-500/10 text-rose-400'
                  }`}>
                  <span className="text-3xl font-black font-mono tracking-tight">
                    {readiness.overall_readiness_score}
                  </span>
                  <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                    / 100
                  </span>
                </div>
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Cognitive Readiness Score
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1E293B] text-slate-300">
                    Confidence: {(readiness.data_completeness * 100).toFixed(0)}%
                  </span>
                </div>
                <h2 className="text-xl font-bold font-mono tracking-wide text-white uppercase">
                  {readiness.rating.replace(/_/g, ' ')}
                </h2>
                <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                  {readiness.explanation}
                </p>
              </div>
            </div>

            {/* Factor Vector Contribution Bars */}
            <div className="w-full lg:w-96 space-y-2.5 bg-[#060913] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex justify-between">
                <span>Vector Breakdown</span>
                <span>Weight</span>
              </div>

              {[
                { label: 'Sleep Recovery', score: readiness.sleep_component, weight: '30%', color: 'bg-indigo-500' },
                { label: 'Circadian Phase', score: readiness.circadian_component, weight: '25%', color: 'bg-sky-400' },
                { label: 'Fatigue Resistance', score: readiness.fatigue_component, weight: '15%', color: 'bg-teal-400' },
                { label: 'Psychological Stress', score: readiness.stress_component, weight: '10%', color: 'bg-amber-400' },
                { label: 'PVT Reaction Time', score: readiness.pvt_component, weight: '20%', color: 'bg-purple-400' }
              ].map(f => (
                <div key={f.label} className="space-y-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-slate-300">{f.label}</span>
                    <span className="text-white font-bold">{f.score.toFixed(0)} <span className="text-slate-500 font-normal">({f.weight})</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-[#1E293B] rounded-full overflow-hidden">
                    <div className={`h-full ${f.color} rounded-full`} style={{ width: `${Math.min(100, f.score)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Grid: Circadian Alertness & Fatigue Monitoring */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Section 2: Circadian Rhythm Projection */}
        <div className="lg:col-span-7 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
            <div className="flex items-center space-x-2.5">
              <Sun className="h-4 w-4 text-amber-400" />
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Two-Process Circadian Alertness Curve (24h)
              </h3>
            </div>
            {circadian && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${circadian.potential_disruption ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}>
                {circadian.potential_disruption ? 'PHASE LAG DETECTED' : 'CIRCADIAN ALIGNED'}
              </span>
            )}
          </div>

          {circadian && (
            <>
              <div className="grid grid-cols-3 gap-3 text-center bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Mission Sol / Hour</p>
                  <p className="text-sm font-bold font-mono text-white mt-0.5">
                    Sol {circadian.mission_day} • {circadian.local_mission_hour.toFixed(1)}h
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Biological Phase</p>
                  <p className="text-sm font-bold font-mono text-[#38BDF8] mt-0.5">
                    {circadian.current_phase.replace(/_/g, ' ')}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Alignment Index</p>
                  <p className="text-sm font-bold font-mono text-emerald-400 mt-0.5">
                    {(circadian.circadian_alignment_index * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* 24-hour Projected Alertness Curve */}
              <div className="h-56 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={circadian.alertness_curve_24h}>
                    <defs>
                      <linearGradient id="alertnessGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366F1" stopOpacity={0.6} />
                        <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis dataKey="hour" stroke="#64748B" tick={{ fontSize: 10, fill: '#94A3B8' }} unit="h" />
                    <YAxis domain={[0, 100]} stroke="#64748B" tick={{ fontSize: 10, fill: '#94A3B8' }} unit="%" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }}
                      formatter={(val: any) => [`${val}%`, 'Alertness']}
                    />
                    <Area type="monotone" dataKey="alertness_score" stroke="#6366F1" strokeWidth={2} fillOpacity={1} fill="url(#alertnessGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>

        {/* Section 3: Fatigue & Autonomic Biomarkers */}
        <div className="lg:col-span-5 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
            <div className="flex items-center space-x-2.5">
              <HeartPulse className="h-4 w-4 text-rose-400" />
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Autonomic Fatigue & Stress
              </h3>
            </div>
            {fatigue && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${fatigue.fatigue_level === 'NORMAL'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : fatigue.fatigue_level === 'ELEVATED'
                    ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                }`}>
                {fatigue.fatigue_level} FATIGUE
              </span>
            )}
          </div>

          {fatigue && sleep && stress && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2.5">
                <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Sleep Debt (Last 24h)</p>
                  <p className="text-base font-bold font-mono text-white mt-0.5">
                    {sleep.daily_deficit_hours.toFixed(1)} <span className="text-xs text-slate-400 font-normal">hrs</span>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-1">Cumul: {sleep.cumulative_sleep_debt_hours.toFixed(1)}h</p>
                </div>

                <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                  <p className="text-[10px] font-mono text-slate-400 uppercase">HRV RMSSD</p>
                  <p className="text-base font-bold font-mono text-teal-400 mt-0.5">
                    {fatigue.hrv_rmssd_ms || 48} <span className="text-xs text-slate-400 font-normal">ms</span>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-1">HR: {fatigue.heart_rate_bpm || 68} bpm</p>
                </div>
              </div>

              {/* Stress Trend LineChart */}
              <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">12h Stress Metric Trend</span>
                  <span className="text-[10px] font-mono text-sky-400 font-bold">
                    Score: {stress.current_stress_score || 'N/A'}
                  </span>
                </div>
                <div className="h-28 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stress.historical_trend}>
                      <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
                      <XAxis dataKey="timestamp_hour" stroke="#64748B" tick={{ fontSize: 9, fill: '#94A3B8' }} unit="h" />
                      <YAxis domain={[0, 100]} stroke="#64748B" tick={{ fontSize: 9, fill: '#94A3B8' }} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '10px', fontFamily: 'monospace' }}
                      />
                      <Line type="monotone" dataKey="stress_score" stroke="#F59E0B" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Section 4: Interactive PVT Battery Component */}
      <PVTTestInterface
        astronautId={selectedAstronautId}
        onSessionComplete={handleSessionComplete}
      />

      {/* Section 5: Historical PVT Sessions Ledger */}
      {pvtHistory && pvtHistory.sessions.length > 0 && (
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B] mb-4">
            <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              Psychomotor Vigilance Test (PVT) History ({pvtHistory.total_sessions_completed} Recorded)
            </h3>
            <span className="text-xs font-mono text-slate-400">
              Historical Avg RT: <strong className="text-white">{pvtHistory.historical_avg_reaction_time_ms} ms</strong>
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-[#1E293B] text-slate-400 text-[10px] uppercase">
                  <th className="py-2 px-3">Session ID</th>
                  <th className="py-2 px-3">Mean RT</th>
                  <th className="py-2 px-3">Median RT</th>
                  <th className="py-2 px-3">Lapses</th>
                  <th className="py-2 px-3">False Starts</th>
                  <th className="py-2 px-3">Performance</th>
                  <th className="py-2 px-3">Completed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B]/60 text-slate-300">
                {pvtHistory.sessions.map(s => (
                  <tr key={s.session_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2 px-3 font-bold text-sky-400">{s.session_id}</td>
                    <td className="py-2 px-3">{s.avg_reaction_time_ms} ms</td>
                    <td className="py-2 px-3">{s.median_reaction_time_ms} ms</td>
                    <td className="py-2 px-3">
                      <span className={s.lapses_count > 0 ? 'text-amber-400 font-bold' : 'text-emerald-400'}>
                        {s.lapses_count}
                      </span>
                    </td>
                    <td className="py-2 px-3">{s.false_starts_count}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${s.performance_rating === 'OPTIMAL' ? 'bg-emerald-500/20 text-emerald-400' :
                          s.performance_rating === 'NORMAL' ? 'bg-sky-500/20 text-sky-400' :
                            'bg-rose-500/20 text-rose-400'
                        }`}>
                        {s.performance_rating}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-slate-500">{new Date(s.completed_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

