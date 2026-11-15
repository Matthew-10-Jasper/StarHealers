import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Activity, Clock, SlidersHorizontal } from 'lucide-react';

export default function VitalsChart({
  historicalData,
  selectedMetric,
  onSelectMetric,
  timeRange,
  onChangeTimeRange,
  astronaut,
}) {
  const [chartType, setChartType] = useState('area'); // 'area' | 'line'

  const timeRanges = [
    { id: '1h', label: 'Last 1 Hour' },
    { id: '24h', label: 'Last 24 Hours' },
    { id: '7d', label: 'Last 7 Days' },
    { id: 'full', label: 'Full Mission History' },
  ];

  const metrics = [
    { id: 'heartRate', label: 'Heart Rate', unit: 'bpm', color: '#00F0FF' },
    { id: 'hrv', label: 'HRV (RMSSD)', unit: 'ms', color: '#3B82F6' },
    { id: 'spo2', label: 'SpO2', unit: '%', color: '#22C55E' },
    { id: 'stress', label: 'Stress Score', unit: 'pts', color: '#F59E0B' },
  ];

  const currentMetric = metrics.find((m) => m.id === selectedMetric) || metrics[0];

  const isNoData = !historicalData || historicalData.length === 0 || historicalData[0][selectedMetric] === null;

  return (
    <div className="glass-panel rounded-xl p-5 border border-slate-800">
      {/* Chart Control Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-5 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-950/40 border border-cyan-800/40 text-cyan-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              <span>Telemetry Historical Analysis</span>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
                Palette 2: Cyan & Blue
              </span>
            </h3>
            <p className="text-xs font-mono text-slate-400">
              Astronaut: {astronaut.name} ({astronaut.id}) | Monitored Metric: {currentMetric.label}
            </p>
          </div>
        </div>

        {/* Filters and Time Ranges */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Metric Selector Buttons */}
          <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            {metrics.map((m) => (
              <button
                key={m.id}
                onClick={() => onSelectMetric(m.id)}
                className={`px-2.5 py-1 rounded transition ${
                  selectedMetric === m.id
                    ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {m.label.split(' ')[0]}
              </button>
            ))}
          </div>

          {/* Time Range Selector */}
          <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-slate-400 ml-1.5 mr-0.5" />
            {timeRanges.map((tr) => (
              <button
                key={tr.id}
                onClick={() => onChangeTimeRange(tr.id)}
                className={`px-2 py-1 rounded transition text-[11px] ${
                  timeRange === tr.id
                    ? 'bg-blue-600/30 text-blue-300 font-semibold border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tr.id.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recharts Canvas */}
      <div className="h-72 w-full">
        {isNoData ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 font-mono text-xs gap-2">
            <div className="p-3 rounded-full bg-slate-900 border border-slate-800 text-slate-400">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <span>No continuous telemetry samples recorded for {astronaut.name} in this time window.</span>
            <span className="text-[10px] text-slate-600">Sensor status: Offline / Recalibrating</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historicalData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis
                dataKey="time"
                stroke="#64748B"
                tick={{ fontSize: 11, fontFamily: 'monospace' }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis
                stroke="#64748B"
                tick={{ fontSize: 11, fontFamily: 'monospace' }}
                tickLine={{ stroke: '#334155' }}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0F172A',
                  borderColor: '#334155',
                  borderRadius: '8px',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                  fontSize: '12px',
                }}
                labelStyle={{ color: '#94A3B8', fontFamily: 'monospace', fontWeight: 600 }}
                formatter={(value) => [`${value} ${currentMetric.unit}`, currentMetric.label]}
              />
              <Area
                type="monotone"
                dataKey={selectedMetric}
                name={currentMetric.label}
                stroke={currentMetric.color}
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#cyanGradient)"
                dot={timeRange === '1h'}
                activeDot={{ r: 5, fill: '#00F0FF', stroke: '#FFFFFF', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Chart Legend and Metadata Footer */}
      <div className="flex flex-wrap items-center justify-between text-xs font-mono text-slate-400 mt-4 pt-3 border-t border-slate-800">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-0.5 bg-cyan-400 rounded-full inline-block" />
            <span className="text-slate-300">Live Reading ({currentMetric.unit})</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-600 inline-block" />
            <span>Time Window: {timeRange.toUpperCase()}</span>
          </div>
        </div>
        <div className="text-[11px] text-slate-500">
          Source: <span className="text-cyan-400">SIMULATED TELEMETRY</span> (NASA Mars Bio-Baseline Model)
        </div>
      </div>
    </div>
  );
}
