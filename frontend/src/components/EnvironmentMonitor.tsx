import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Wind, Thermometer, Radio, Clock, AlertCircle, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { EnvironmentStatus, DataQualityContext } from '../types/mission';
import { TelemetryEChart } from './telemetry/TelemetryEChart';

interface EnvironmentMonitorProps {
  environment: EnvironmentStatus;
  dataQuality: DataQualityContext;
}

export const EnvironmentMonitor: React.FC<EnvironmentMonitorProps> = ({ environment, dataQuality }) => {
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [chartEngine, setChartEngine] = useState<'echarts' | 'recharts'>('echarts');

  useEffect(() => {
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    const pressureVal = environment.observed_parameters['CABIN_PRESSURE'] !== undefined
      ? parseFloat(environment.observed_parameters['CABIN_PRESSURE'])
      : null;

    const co2Val = environment.observed_parameters['CO2_CONCENTRATION'] !== undefined
      ? parseFloat(environment.observed_parameters['CO2_CONCENTRATION'])
      : null;

    const radVal = environment.observed_parameters['RADIATION'] !== undefined
      ? parseFloat(environment.observed_parameters['RADIATION'])
      : null;

    setHistoryData((prev) => {
      const next = [...prev, { time: timeStr, pressure: pressureVal, co2: co2Val, radiation: radVal }];
      return next.slice(-20); // Keep last 20 telemetry ticks
    });
  }, [environment]);

  const observed = environment.observed_parameters;

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#1E293B] gap-2">
        <div className="flex items-center space-x-2">
          <Wind className="h-5 w-5 text-amber-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section E • Spacecraft Environment Telemetry Monitor
          </h2>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {dataQuality.telemetry_completeness && (
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${dataQuality.telemetry_completeness === 'COMPLETE' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'}`}>
              COMPLETENESS: {dataQuality.telemetry_completeness}
            </span>
          )}
          {dataQuality.telemetry_freshness && (
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${dataQuality.telemetry_freshness === 'FRESH' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-rose-500/20 text-rose-400 border border-rose-500/40'}`}>
              FRESHNESS: {dataQuality.telemetry_freshness}
            </span>
          )}
          <span className="text-xs font-mono text-slate-400">
            LAST TELEMETRY: {dataQuality.last_telemetry_timestamp ? new Date(dataQuality.last_telemetry_timestamp).toLocaleTimeString() : 'AWAITING_INGEST'}
          </span>
        </div>
      </div>

      {/* Unknown Parameters Warning Banner */}
      {dataQuality.unknown_parameters.length > 0 && (
        <div className="mt-4 p-3 rounded-lg bg-slate-900/80 border border-slate-700/80 flex items-start space-x-3 text-xs font-mono">
          <AlertCircle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="text-amber-400 font-bold">MISSING PARAMETERS REMAIN STRICTLY UNKNOWN: </span>
            <span className="text-slate-300">
              {dataQuality.unknown_parameters.join(', ')} (no synthetic value fabricated without verified sensor feed).
            </span>
          </div>
        </div>
      )}

      {/* Primary Environmental Parameter Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mt-4">
        {/* Cabin Pressure */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
            Cabin Pressure
          </div>
          <div className="mt-1 text-lg font-bold font-mono text-slate-100">
            {observed['CABIN_PRESSURE'] !== undefined ? `${observed['CABIN_PRESSURE']} kPa` : 'UNKNOWN'}
          </div>
          <div className="text-[11px] font-mono mt-0.5 text-slate-400">
            Status: <span className={environment.cabin_pressure_status === 'NOMINAL' ? 'text-emerald-400' : 'text-amber-400 font-semibold'}>{environment.cabin_pressure_status}</span>
          </div>
        </div>

        {/* CO2 Concentration */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
            CO2 Partial Pressure
          </div>
          <div className="mt-1 text-lg font-bold font-mono text-slate-100">
            {observed['CO2_CONCENTRATION'] !== undefined ? `${observed['CO2_CONCENTRATION']} mmHg` : 'UNKNOWN'}
          </div>
          <div className="text-[11px] font-mono mt-0.5 text-slate-400">
            Status: <span className={environment.co2_status === 'NOMINAL' ? 'text-emerald-400' : 'text-amber-400 font-semibold'}>{environment.co2_status}</span>
          </div>
        </div>

        {/* Radiation Observation */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
            Radiation Dosimetry
          </div>
          <div className="mt-1 text-lg font-bold font-mono text-slate-100">
            {observed['RADIATION'] !== undefined ? `${observed['RADIATION']} mSv/d` : 'UNKNOWN'}
          </div>
          <div className="text-[11px] font-mono mt-0.5 text-slate-400">
            Status: <span className={environment.radiation_status === 'NOMINAL' ? 'text-emerald-400' : 'text-crimson-400 font-semibold'}>{environment.radiation_status}</span>
          </div>
        </div>

        {/* ECLSS Life-Support Loop */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
            Life-Support (ECLSS)
          </div>
          <div className="mt-1 text-base font-bold font-mono truncate text-slate-100">
            {environment.life_support_status}
          </div>
          <div className="text-[11px] font-mono mt-0.5 text-slate-500">
            O2: {observed['O2_PERCENTAGE'] !== undefined ? `${observed['O2_PERCENTAGE']}%` : 'UNKNOWN'}
          </div>
        </div>

        {/* Habitat Structure */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
            Habitat Structural
          </div>
          <div className="mt-1 text-base font-bold font-mono truncate text-slate-100">
            {environment.habitat_status}
          </div>
          <div className="text-[11px] font-mono mt-0.5 text-slate-500">
            Hull Integrity
          </div>
        </div>
      </div>

      {/* Real-Time Telemetry Trend Chart with Multi-Engine Support */}
      <div className="mt-6 pt-4 border-t border-[#1E293B]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
              Real-Time Environmental Trend History
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
              {chartEngine === 'echarts' ? 'ECharts 3-Axis Zoom' : 'Recharts Standard'}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <div className="flex bg-[#060913] p-0.5 rounded-lg border border-[#1E293B]">
              <button
                onClick={() => setChartEngine('echarts')}
                className={`px-2.5 py-1 text-[11px] font-mono rounded transition-all ${chartEngine === 'echarts'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                  }`}
              >
                ECharts (Multi-Axis)
              </button>
              <button
                onClick={() => setChartEngine('recharts')}
                className={`px-2.5 py-1 text-[11px] font-mono rounded transition-all ${chartEngine === 'recharts'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                  }`}
              >
                Recharts
              </button>
            </div>
          </div>
        </div>

        {chartEngine === 'echarts' ? (
          <TelemetryEChart data={historyData} height={260} />
        ) : (
          <div className="h-44 w-full bg-[#060913] p-2 rounded-lg border border-[#1E293B]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748B" tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', fontSize: '11px', color: '#F8FAFC' }}
                />
                <Line type="monotone" dataKey="pressure" stroke="#22D3EE" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="co2" stroke="#FBBF24" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="radiation" stroke="#F87171" strokeWidth={2} dot={false} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

