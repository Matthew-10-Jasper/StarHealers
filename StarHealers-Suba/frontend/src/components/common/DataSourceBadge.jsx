import React from 'react';
import { Cpu, Database, Activity, Edit3 } from 'lucide-react';

export default function DataSourceBadge({ source, quality }) {
  const src = (source || 'SIMULATED').toUpperCase();

  const configs = {
    'SIMULATED': {
      label: 'SIMULATED',
      icon: Cpu,
      color: 'text-cyan-400 bg-cyan-950/40 border-cyan-800/40',
    },
    'RESEARCH DATASET': {
      label: 'RESEARCH DATASET',
      icon: Database,
      color: 'text-purple-400 bg-purple-950/40 border-purple-800/40',
    },
    'CONNECTED SENSOR': {
      label: 'CONNECTED SENSOR',
      icon: Activity,
      color: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40',
    },
    'MANUAL INPUT': {
      label: 'MANUAL INPUT',
      icon: Edit3,
      color: 'text-amber-400 bg-amber-950/40 border-amber-800/40',
    },
  };

  const current = configs[src] || configs['SIMULATED'];
  const Icon = current.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono tracking-wider border ${current.color}`}
      title={quality ? `Data Quality: ${quality}` : undefined}
    >
      <Icon className="w-3 h-3" />
      <span>{current.label}</span>
      {quality && (
        <span className="text-slate-400 border-l border-slate-700/60 pl-1.5 ml-0.5">
          {quality}
        </span>
      )}
    </span>
  );
}
