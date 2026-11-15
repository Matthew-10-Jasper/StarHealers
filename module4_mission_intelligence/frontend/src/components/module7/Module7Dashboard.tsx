import React, { useState, useEffect, useCallback } from 'react';
import {
  apiM7,
  CompositeRisk,
  RadiationOverview,
  CO2Overview,
  CabinTelemetry,
  HazardAlert
} from '../../services/modulesApi';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid
} from 'recharts';
import {
  Sun, Shield, AlertTriangle, Wind, Gauge,
  RefreshCw, CheckCircle2, Flame, ShieldAlert,
  Info, Check, HelpCircle
} from 'lucide-react';

export const Module7Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<CompositeRisk | null>(null);
  const [radiation, setRadiation] = useState<RadiationOverview | null>(null);
  const [co2, setCO2] = useState<CO2Overview | null>(null);
  const [cabin, setCabin] = useState<CabinTelemetry | null>(null);
  const [alerts, setAlerts] = useState<HazardAlert[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [ackOfficer, setAckOfficer] = useState<string>('Cmdr. Sarah Vance');
  const [ackTargetId, setAckTargetId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const [ovData, radData, co2Data, cabData, altData] = await Promise.all([
        apiM7.getOverview(),
        apiM7.getRadiation(),
        apiM7.getCO2(),
        apiM7.getCabin(),
        apiM7.getAlerts()
      ]);
      setOverview(ovData);
      setRadiation(radData);
      setCO2(co2Data);
      setCabin(cabData);
      setAlerts(altData);
    } catch (err) {
      console.error('Failed to load Module 7 data:', err);
    } finally {
      setIsRefreshing(false);
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await apiM7.acknowledgeAlert(alertId, ackOfficer, 'Acknowledged from Space Environment Console');
      setAckTargetId(null);
      await loadData();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Subsystem Header */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-[#EAB308]/30 text-[#EAB308]">
              <Sun className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#EAB308]/20 text-[#F97316] border border-[#EAB308]/30 font-bold uppercase tracking-wider">
                  MODULE 7
                </span>
                <span className="text-xs font-mono text-slate-400">PORT 8007</span>
              </div>
              <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
                Space Environment, Radiation & Life-Support Integration
              </h1>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={loadData}
              disabled={isRefreshing}
              className="px-3 py-1.5 rounded-lg bg-[#1E293B] hover:bg-slate-800 text-slate-300 font-mono text-xs flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-[#EAB308]' : ''}`} />
              <span>Poll Environmental State</span>
            </button>
          </div>
        </div>
      </div>

      {/* Section 1: Composite Environmental Risk Hero */}
      {overview && (
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 shadow-xl">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="flex items-center space-x-5">
              <div className="relative flex items-center justify-center">
                <div className={`w-28 h-28 rounded-full flex flex-col items-center justify-center border-4 shadow-2xl ${
                  overview.operational_risk_level === 'NOMINAL'
                    ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                    : overview.operational_risk_level === 'MONITORING_REQUIRED'
                    ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                    : overview.operational_risk_level === 'CONTINGENCY'
                    ? 'border-orange-500 bg-orange-500/10 text-orange-400'
                    : 'border-rose-500 bg-rose-500/10 text-rose-400'
                }`}>
                  <span className="text-3xl font-black font-mono tracking-tight">
                    {overview.overall_risk_index}
                  </span>
                  <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                    Risk / 100
                  </span>
                </div>
              </div>
              <div className="space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Composite Spaceflight Environmental Index
                  </span>
                  {overview.active_hazards_count > 0 && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30 font-bold">
                      {overview.active_hazards_count} ACTIVE ALERTS
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-bold font-mono tracking-wide text-white uppercase">
                  {overview.operational_risk_level.replace(/_/g, ' ')}
                </h2>
                <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
                  {overview.summary}
                </p>
              </div>
            </div>

            {/* Component Risk Gauges */}
            <div className="w-full lg:w-96 space-y-2.5 bg-[#060913] p-4 rounded-xl border border-[#1E293B]">
              <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex justify-between">
                <span>Domain Risk Vectors</span>
                <span>Risk Level</span>
              </div>

              {[
                { label: 'Radiation Risk', score: overview.radiation_risk_score, weight: '40%', color: 'bg-amber-500' },
                { label: 'Atmospheric CO2 Risk', score: overview.co2_risk_score, weight: '35%', color: 'bg-orange-500' },
                { label: 'Cabin Pressure Risk', score: overview.cabin_risk_score, weight: '25%', color: 'bg-sky-500' }
              ].map(r => (
                <div key={r.label} className="space-y-1">
                  <div className="flex justify-between text-[11px] font-mono">
                    <span className="text-slate-300">{r.label}</span>
                    <span className="text-white font-bold">{r.score.toFixed(0)} <span className="text-slate-500 font-normal">({r.weight})</span></span>
                  </div>
                  <div className="h-1.5 w-full bg-[#1E293B] rounded-full overflow-hidden">
                    <div className={`h-full ${r.color} rounded-full`} style={{ width: `${Math.min(100, r.score)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Grid: Space Radiation & CO2 Life Support */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Section 2: Space Radiation Subsystem */}
        <div className="lg:col-span-7 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
            <div className="flex items-center space-x-2.5">
              <Flame className="h-4 w-4 text-amber-400" />
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Space Radiation Exposure & SPE Flare Monitor
              </h3>
            </div>
            {radiation && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-[#EAB308] border border-amber-500/30 font-bold">
                {radiation.provenance}
              </span>
            )}
          </div>

          {radiation && (
            <>
              {radiation.active_spe_event && (
                <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-500/40 flex items-start space-x-2.5 text-xs text-amber-200">
                  <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-white">SOLAR PARTICLE EVENT IN PROGRESS: </span>
                    Dose rates elevated from Weibull flare dynamics. Current shielding: {radiation.shielding_thickness_g_cm2} g/cm² ({radiation.shielding_material}).
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 bg-[#060913] p-3 rounded-lg border border-[#1E293B] text-center">
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Cumulative Dose</p>
                  <p className="text-base font-bold font-mono text-white mt-0.5">
                    {radiation.cumulative_dose_msv.toFixed(2)} <span className="text-xs text-slate-400 font-normal">mSv</span>
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Current Dose Rate</p>
                  <p className="text-base font-bold font-mono text-amber-400 mt-0.5">
                    {radiation.current_dose_rate_msv_h.toFixed(3)} <span className="text-xs text-slate-400 font-normal">mSv/h</span>
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">30-Day Limit (250mSv)</p>
                  <p className="text-base font-bold font-mono text-sky-400 mt-0.5">
                    {radiation.thirty_day_limit_pct.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Career Limit (1000mSv)</p>
                  <p className="text-base font-bold font-mono text-emerald-400 mt-0.5">
                    {radiation.career_limit_pct.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Radiation Timeline Chart */}
              <div className="h-52 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={radiation.time_series}>
                    <defs>
                      <linearGradient id="radGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#EAB308" stopOpacity={0.7}/>
                        <stop offset="95%" stopColor="#F97316" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis dataKey="hour" stroke="#64748B" tick={{ fontSize: 10, fill: '#94A3B8' }} unit="h" />
                    <YAxis stroke="#64748B" tick={{ fontSize: 10, fill: '#94A3B8' }} unit="mSv" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }}
                      formatter={(val: any) => [`${val} mSv`, 'Total Dose']}
                    />
                    <Area type="monotone" dataKey="total_cumulative_msv" stroke="#EAB308" strokeWidth={2} fillOpacity={1} fill="url(#radGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>

        {/* Section 3: CO2 Atmospheric Monitoring */}
        <div className="lg:col-span-5 bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
            <div className="flex items-center space-x-2.5">
              <Wind className="h-4 w-4 text-[#F97316]" />
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Atmospheric CO2 & Scrubbing
              </h3>
            </div>
            {co2 && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                co2.status === 'NOMINAL' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                co2.status === 'ELEVATED' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}>
                {co2.status}
              </span>
            )}
          </div>

          {co2 && (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2.5">
                <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                  <p className="text-[10px] font-mono text-slate-400 uppercase">ppCO2 (Partial Pressure)</p>
                  <p className={`text-lg font-bold font-mono mt-0.5 ${
                    co2.ppco2_mmhg >= 5.0 ? 'text-rose-400' : co2.ppco2_mmhg >= 3.0 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {co2.ppco2_mmhg} <span className="text-xs text-slate-400 font-normal">mmHg</span>
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-1">Conc: {co2.current_co2_pct}%</p>
                </div>

                <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                  <p className="text-[10px] font-mono text-slate-400 uppercase">Scrubber Efficiency</p>
                  <p className={`text-lg font-bold font-mono mt-0.5 ${
                    co2.scrubber_efficiency_pct < 60 ? 'text-rose-400' : co2.scrubber_efficiency_pct < 85 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {co2.scrubber_efficiency_pct}%
                  </p>
                  <p className="text-[10px] font-mono text-slate-500 mt-1">Dual-Bed CDRA</p>
                </div>
              </div>

              {/* CO2 LineChart */}
              <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Atmospheric Accumulation Trend</span>
                  <span className="text-[10px] font-mono text-amber-400">Limit: 3.0 mmHg</span>
                </div>
                <div className="h-28 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={co2.time_series}>
                      <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" />
                      <XAxis dataKey="hour" stroke="#64748B" tick={{ fontSize: 9, fill: '#94A3B8' }} unit="h" />
                      <YAxis stroke="#64748B" tick={{ fontSize: 9, fill: '#94A3B8' }} unit="mmHg" />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '10px', fontFamily: 'monospace' }}
                      />
                      <Line type="monotone" dataKey="ppco2_mmhg" stroke="#F97316" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Section 4: Module 4 Cabin Telemetry Cross-Integration */}
      {cabin && (
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
            <div className="flex items-center space-x-2.5">
              <Gauge className="h-4 w-4 text-sky-400" />
              <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                Live Module 4 Mission Environment Cross-Verification
              </h3>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">
                Freshness: {cabin.telemetry_freshness}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                Completeness: {cabin.completeness}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            {/* Cabin Pressure (Verified) */}
            <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 uppercase">
                <span>Cabin Pressure</span>
                <span className="text-emerald-400 font-bold">VERIFIED</span>
              </div>
              <p className="text-lg font-bold font-mono text-white mt-1">
                {cabin.cabin_pressure_kpa !== null ? `${cabin.cabin_pressure_kpa} kPa` : 'UNKNOWN'}
              </p>
              <p className="text-[10px] font-mono text-emerald-400 mt-0.5">Status: {cabin.cabin_pressure_status}</p>
            </div>

            {/* O2 Concentration (Truthfully Missing) */}
            <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]/70">
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 uppercase">
                <span>O2 Concentration</span>
                <span className="text-slate-500 font-bold">UNMEASURED</span>
              </div>
              <p className="text-base font-bold font-mono text-slate-500 mt-1">
                DATA UNAVAILABLE
              </p>
              <p className="text-[10px] font-mono text-slate-500 mt-0.5">Telemetry offline</p>
            </div>

            {/* Cabin Temperature */}
            <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]/70">
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 uppercase">
                <span>Temperature</span>
                <span className="text-slate-500 font-bold">UNMEASURED</span>
              </div>
              <p className="text-base font-bold font-mono text-slate-500 mt-1">
                DATA UNAVAILABLE
              </p>
              <p className="text-[10px] font-mono text-slate-500 mt-0.5">Sensor pending link</p>
            </div>

            {/* Relative Humidity */}
            <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]/70">
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-400 uppercase">
                <span>Humidity</span>
                <span className="text-slate-500 font-bold">UNMEASURED</span>
              </div>
              <p className="text-base font-bold font-mono text-slate-500 mt-1">
                DATA UNAVAILABLE
              </p>
              <p className="text-[10px] font-mono text-slate-500 mt-0.5">Sensor pending link</p>
            </div>
          </div>
        </div>
      )}

      {/* Section 5: Hazard Alerts & Interactive Acknowledgement */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]">
          <div className="flex items-center space-x-2.5">
            <ShieldAlert className="h-4 w-4 text-amber-400" />
            <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
              Space Hazard Alert Triage ({alerts.length} Total, {alerts.filter(a => !a.acknowledged).length} Active)
            </h3>
          </div>
        </div>

        <div className="space-y-2.5">
          {alerts.map(a => (
            <div
              key={a.alert_id}
              className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-colors ${
                a.acknowledged
                  ? 'bg-[#060913]/60 border-[#1E293B] opacity-75'
                  : a.severity === 'CRITICAL'
                  ? 'bg-rose-950/20 border-rose-500/50'
                  : a.severity === 'WARNING'
                  ? 'bg-amber-950/20 border-amber-500/50'
                  : 'bg-slate-900 border-slate-700'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                    a.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' :
                    a.severity === 'WARNING' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-slate-700 text-slate-300'
                  }`}>
                    {a.severity}
                  </span>
                  <span className="font-mono text-xs font-bold text-white">{a.alert_id}</span>
                  <span className="text-[10px] font-mono text-slate-400">[{a.source_module}]</span>
                </div>
                <p className="text-xs text-slate-300 font-mono leading-relaxed">
                  {a.message}
                </p>
                {a.acknowledged && (
                  <p className="text-[10px] font-mono text-emerald-400 flex items-center space-x-1">
                    <Check className="h-3 w-3" />
                    <span>Acknowledged by {a.acknowledged_by} ({new Date(a.acknowledged_at || '').toLocaleTimeString()})</span>
                  </p>
                )}
              </div>

              {!a.acknowledged && (
                <div className="shrink-0 flex items-center space-x-2">
                  {ackTargetId === a.alert_id ? (
                    <div className="flex items-center space-x-1.5">
                      <input
                        type="text"
                        value={ackOfficer}
                        onChange={e => setAckOfficer(e.target.value)}
                        placeholder="Officer Callsign"
                        className="px-2 py-1 bg-[#060913] border border-slate-700 rounded text-xs font-mono text-white w-36"
                      />
                      <button
                        onClick={() => handleAcknowledge(a.alert_id)}
                        className="px-3 py-1 bg-amber-500 hover:bg-amber-400 text-black font-mono font-bold text-xs rounded transition-colors"
                      >
                        Confirm
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setAckTargetId(a.alert_id)}
                      className="px-3 py-1.5 rounded-lg bg-[#1E293B] hover:bg-slate-800 text-amber-400 border border-amber-500/30 font-mono text-xs font-bold flex items-center space-x-1 transition-colors"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>Acknowledge</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

