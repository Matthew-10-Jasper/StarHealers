import React, { useState } from 'react';
import VitalsChart from '../modules/Module1Vitals/VitalsChart';
import DataSourceBadge from '../common/DataSourceBadge';
import { History, Download, Filter, Search, Calendar, Activity } from 'lucide-react';

export default function HealthHistoryView({
  astronaut,
  historicalData,
  timeRange,
  onChangeTimeRange,
}) {
  const [selectedMetric, setSelectedMetric] = useState('heartRate');
  const [searchLog, setSearchLog] = useState('');

  const isNoData = !historicalData || historicalData.length === 0 || historicalData[0].heartRate === null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <History className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-white font-sans tracking-wide">
              Historical Physiological Telemetry Archive
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
              Astronaut: {astronaut.name} ({astronaut.id})
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Persistent historical biometric records, multi-frequency time-series graphs, and telemetry logs.
          </p>
        </div>

        <button
          onClick={() => alert(`Exporting telemetry archive for ${astronaut.id} in JSON / CSV format...`)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-500 text-xs font-mono text-slate-200 transition"
        >
          <Download className="w-3.5 h-3.5 text-cyan-400" />
          <span>Export Telemetry (CSV)</span>
        </button>
      </div>

      {/* Recharts Trend Component */}
      <VitalsChart
        historicalData={historicalData}
        selectedMetric={selectedMetric}
        onSelectMetric={setSelectedMetric}
        timeRange={timeRange}
        onChangeTimeRange={onChangeTimeRange}
        astronaut={astronaut}
      />

      {/* Historical Telemetry Data Log Table */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Time-Indexed Biometric Telemetry Packets</span>
          </h3>
          <span className="text-xs font-mono text-slate-400">
            Window: {timeRange.toUpperCase()} | Total Packets: {isNoData ? 0 : historicalData.length}
          </span>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 text-[10px] uppercase">
              <tr>
                <th className="py-2.5 px-3">Time Index</th>
                <th className="py-2.5 px-3">Heart Rate</th>
                <th className="py-2.5 px-3">HRV (RMSSD)</th>
                <th className="py-2.5 px-3">SpO2</th>
                <th className="py-2.5 px-3">Skin Temp</th>
                <th className="py-2.5 px-3">Stress Score</th>
                <th className="py-2.5 px-3">Data Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 bg-slate-950/40">
              {isNoData ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500 font-mono text-xs">
                    No telemetry records available for this astronaut in the selected range.
                  </td>
                </tr>
              ) : (
                historicalData.slice(0, 10).map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/50">
                    <td className="py-2.5 px-3 text-slate-300 font-semibold">{row.time}</td>
                    <td className="py-2.5 px-3 text-cyan-300 font-bold">{row.heartRate} bpm</td>
                    <td className="py-2.5 px-3 text-blue-300">{row.hrv} ms</td>
                    <td className="py-2.5 px-3 text-emerald-300">{row.spo2}%</td>
                    <td className="py-2.5 px-3 text-slate-200">{row.temperature} °C</td>
                    <td className="py-2.5 px-3 text-amber-300">{row.stress} pts</td>
                    <td className="py-2.5 px-3">
                      <DataSourceBadge source={row.source} quality="HIGH" />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
