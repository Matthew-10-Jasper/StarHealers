import React from 'react';
import {
  Heart,
  Activity,
  Droplet,
  Wind,
  Thermometer,
  Zap,
  Moon,
  TrendingUp,
  TrendingDown,
  Minus,
  HelpCircle,
} from 'lucide-react';
import SeverityBadge from './SeverityBadge';
import DataSourceBadge from './DataSourceBadge';

export default function MetricCard({
  metricKey,
  metricDef,
  reading,
  isSelected,
  onClick,
}) {
  const isNoData = !reading || reading.value === null || reading.value === undefined;

  const iconMap = {
    heartRate: Heart,
    hrv: Activity,
    bloodPressure: Activity,
    spo2: Wind,
    temperature: Thermometer,
    glucose: Zap,
    sleep: Moon,
    hydration: Droplet,
    stress: Activity,
  };

  const Icon = iconMap[metricKey] || Activity;

  // Determine border and accent styling based on severity
  const getSeverityStyle = (status) => {
    switch (status) {
      case 'CRITICAL':
        return 'border-rose-500/50 hover:border-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.15)]';
      case 'WARNING':
        return 'border-amber-500/50 hover:border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.15)]';
      case 'NORMAL':
        return 'border-slate-800 hover:border-cyan-500/40 hover:shadow-cyan-glow';
      default:
        return 'border-slate-800/80 hover:border-slate-700 opacity-80';
    }
  };

  // Render value display
  const renderValue = () => {
    if (isNoData) {
      return (
        <div className="flex items-center gap-1.5 py-1 text-slate-500 font-mono">
          <HelpCircle className="w-5 h-5" />
          <span className="text-xl font-bold tracking-tight">NO DATA</span>
        </div>
      );
    }

    if (metricKey === 'bloodPressure') {
      return (
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl lg:text-3xl font-bold font-mono tracking-tight text-white">
            {reading.systolic}/{reading.diastolic}
          </span>
          <span className="text-xs font-mono text-cyan-400/80">{metricDef.unit}</span>
        </div>
      );
    }

    return (
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl lg:text-3xl font-bold font-mono tracking-tight text-white">
          {reading.value}
        </span>
        <span className="text-xs font-mono text-cyan-400/80">{metricDef.unit}</span>
      </div>
    );
  };

  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick && onClick();
        }
      }}
      className={`glass-card rounded-xl p-4 cursor-pointer transition relative group ${
        isSelected
          ? 'border-cyan-400 ring-1 ring-cyan-400/50 bg-slate-900/90 shadow-cyan-glow'
          : getSeverityStyle(reading?.status)
      }`}
    >
      {/* Header: Label & Icon */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div
            className={`p-1.5 rounded-lg border ${
              reading?.status === 'CRITICAL'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                : reading?.status === 'WARNING'
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
            }`}
          >
            <Icon className="w-4 h-4" />
          </div>
          <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition">
            {metricDef.label}
          </span>
        </div>
        <SeverityBadge severity={reading?.status || 'NO_DATA'} size="sm" showIcon={false} />
      </div>

      {/* Numerical Value & Unit */}
      <div className="mt-3 mb-2">{renderValue()}</div>

      {/* Reference Range Indicator */}
      <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between mb-3 border-t border-slate-800/80 pt-2">
        <span>Ref Range:</span>
        <span className="text-slate-300">
          {metricKey === 'bloodPressure'
            ? '90-130 / 60-85'
            : `${metricDef.normalMin ?? '—'} - ${metricDef.normalMax ?? '—'} ${metricDef.unit}`}
        </span>
      </div>

      {/* Footer: Source badge & Timestamp */}
      <div className="flex items-center justify-between gap-1 pt-1 border-t border-slate-800/60">
        <DataSourceBadge
          source={reading?.source || 'SIMULATED'}
          quality={reading?.quality}
        />
        <span className="text-[10px] font-mono text-slate-400">
          {reading?.timestamp ? reading.timestamp.split('T')[1].substring(0, 5) + ' UTC' : '—'}
        </span>
      </div>

      {/* Selected Indicator Dot */}
      {isSelected && (
        <span className="absolute top-2 right-2 flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
      )}
    </div>
  );
}
