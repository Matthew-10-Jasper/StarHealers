import React from 'react';
import { AlertTriangle, AlertCircle, Info, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { MissionDeviation, DeviationSeverity } from '../types/mission';

interface DeviationMonitorProps {
  deviations: MissionDeviation[];
}

export const DeviationMonitor: React.FC<DeviationMonitorProps> = ({ deviations }) => {
  const getSeverityBadge = (sev: DeviationSeverity) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-crimson-950/80 text-crimson-400 border-crimson-500 shadow-crimson-900/30 animate-pulse';
      case 'WARNING':
        return 'bg-amber-950/70 text-amber-400 border-amber-500 shadow-amber-900/20';
      case 'INFO':
        return 'bg-cyan-950/50 text-cyan-400 border-cyan-500/50';
      case 'UNKNOWN':
      default:
        return 'bg-slate-800 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-crimson-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section D • Active Mission Deviation Monitor
          </h2>
        </div>
        <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-[#060913] border border-[#1E293B] text-slate-300">
          COUNT: {deviations.length}
        </span>
      </div>

      {deviations.length === 0 ? (
        <div className="py-8 flex flex-col items-center justify-center text-center">
          <CheckCircle2 className="h-10 w-10 text-emerald-400/60 mb-2" />
          <p className="text-sm font-medium text-slate-300">
            No Active Mission Deviations Detected
          </p>
          <p className="text-xs text-slate-500 font-mono mt-1">
            Verified telemetry remains within planned mission bounds.
          </p>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          {deviations.map((dev) => (
            <div
              key={dev.deviation_id}
              className={`p-4 rounded-lg border transition ${
                dev.severity === 'CRITICAL'
                  ? 'bg-crimson-950/20 border-crimson-500/60'
                  : dev.severity === 'WARNING'
                  ? 'bg-amber-950/20 border-amber-500/60'
                  : 'bg-slate-900/50 border-[#1E293B]'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSeverityBadge(dev.severity)}`}>
                    {dev.severity}
                  </span>
                  <span className="font-mono text-xs font-bold text-slate-200">
                    {dev.deviation_name}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-400 flex items-center space-x-3">
                  <span>CATEGORY: {dev.category}</span>
                  <span>SOURCE: {dev.source}</span>
                  <span>{new Date(dev.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3 pt-3 border-t border-[#1E293B]/60 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase">EXPECTED CONDITION</span>
                  <span className="text-slate-300">{dev.expected_condition}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase">ACTUAL VERIFIED OBSERVATION</span>
                  <span className={dev.severity === 'CRITICAL' ? 'text-crimson-300 font-semibold' : 'text-amber-300 font-semibold'}>
                    {dev.actual_condition}
                  </span>
                </div>
              </div>

              {dev.evidence && Object.keys(dev.evidence).length > 0 && (
                <div className="mt-2 text-[11px] font-mono text-slate-500 bg-[#060913]/60 p-2 rounded border border-[#1E293B]">
                  <span className="text-slate-400 font-semibold">Evidence Payload: </span>
                  {JSON.stringify(dev.evidence)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

