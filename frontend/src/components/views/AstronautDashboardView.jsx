import React from 'react';
import SeverityBadge from '../common/SeverityBadge';
import DataSourceBadge from '../common/DataSourceBadge';
import MetricCard from '../common/MetricCard';
import BodyAnatomySvg from '../modules/Module2BodyMap/BodyAnatomySvg';
import { METRIC_DEFINITIONS, BODY_REGIONS_CONFIG } from '../../data/mockData';
import {
  Activity,
  User,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  Clock,
  HeartPulse,
  Sliders,
} from 'lucide-react';

export default function AstronautDashboardView({
  astronaut,
  mission,
  readings,
  historicalData,
  alerts,
  onNavigateTab,
  onSelectMetric,
}) {
  const activeAlertsForAstro = alerts.filter(
    (a) => a.astronautId === astronaut.id && a.status === 'ACTIVE'
  );

  const regionStatuses = astronaut.bodyRegionStatus || {};

  return (
    <div className="space-y-6">
      {/* Astronaut Header Profile Card */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="relative">
            <img
              src={astronaut.avatar}
              alt={astronaut.name}
              className="w-14 h-14 rounded-xl object-cover border-2 border-slate-700 shadow-md"
            />
            <span className="absolute -bottom-1 -right-1">
              <SeverityBadge severity={astronaut.status} size="sm" showIcon={false} />
            </span>
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h2 className="text-xl font-bold text-white font-sans">{astronaut.name}</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                {astronaut.id}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {astronaut.role}
              </span>
            </div>
            <p className="text-xs text-slate-300 font-sans">
              <strong className="text-slate-400 font-mono">STATUS ASSESSMENT:</strong> {astronaut.statusReason}
            </p>
          </div>
        </div>

        {/* Biometric Vital Baseline Quick Specs */}
        <div className="flex items-center gap-4 text-xs font-mono text-slate-300 p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <div>
            <span className="text-[10px] text-slate-400 block">AGE / BLOOD</span>
            <span className="text-white font-semibold">{astronaut.age} yrs • {astronaut.bloodType}</span>
          </div>
          <div className="border-l border-slate-800 pl-4">
            <span className="text-[10px] text-slate-400 block">BASE RESTING HR</span>
            <span className="text-cyan-400 font-semibold">{astronaut.baseline.restingHr} bpm</span>
          </div>
          <div className="border-l border-slate-800 pl-4">
            <span className="text-[10px] text-slate-400 block">BASE HRV (RMSSD)</span>
            <span className="text-blue-400 font-semibold">{astronaut.baseline.hrv} ms</span>
          </div>
        </div>
      </div>

      {/* Active Critical Alerts Notice (if any) */}
      {activeAlertsForAstro.length > 0 && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-rose-950/40 to-slate-900 border border-rose-500/40 shadow-crimson-glow space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-rose-300 font-semibold text-xs font-mono">
              <ShieldAlert className="w-4 h-4 text-rose-400 animate-pulse" />
              <span>ACTIVE CLINICAL TRIAGE ALERTS FOR {astronaut.name.toUpperCase()}</span>
            </div>
            <button
              onClick={() => onNavigateTab('triage-alerts')}
              className="text-xs font-mono text-rose-300 hover:text-white flex items-center gap-1 underline"
            >
              View Health Alerts <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {activeAlertsForAstro.map((alert) => (
              <div
                key={alert.id}
                className="p-3 rounded-lg bg-slate-950/70 border border-rose-900/60 text-xs"
              >
                <div className="flex items-center justify-between font-mono mb-1">
                  <span className="font-bold text-rose-300">{alert.title}</span>
                  <SeverityBadge severity={alert.severity} size="sm" />
                </div>
                <p className="text-slate-300 text-[11px] font-sans line-clamp-2">{alert.triggerReason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Cockpit Split: Left 6 Core Vitals, Right Interactive Body Map Teaser */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 8 Cols: Quick Vitals Cards */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Primary Physiological Telemetry</span>
            </h3>
            <button
              onClick={() => onNavigateTab('vitals-monitoring')}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
            >
              Open Crew Health <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {['heartRate', 'hrv', 'bloodPressure', 'spo2', 'temperature', 'stress'].map((key) => (
              <MetricCard
                key={key}
                metricKey={key}
                metricDef={METRIC_DEFINITIONS[key]}
                reading={readings?.[key]}
                onClick={() => {
                  onSelectMetric && onSelectMetric(key);
                  onNavigateTab('vitals-monitoring');
                }}
              />
            ))}
          </div>
        </div>

        {/* Right 4 Cols: Anatomical Body Map Card */}
        <div className="lg:col-span-4 glass-panel rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <HeartPulse className="w-4 h-4 text-cyan-400" />
              <span>Anatomical Status</span>
            </h3>
            <button
              onClick={() => onNavigateTab('body-map')}
              className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
            >
              View Body Systems <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="py-2 flex justify-center">
            <BodyAnatomySvg
              regionStatuses={regionStatuses}
              selectedRegion="heart"
              onSelectRegion={() => onNavigateTab('body-map')}
            />
          </div>

          <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-400 text-center">
            Click map to inspect organ telemetry & alerts
          </div>
        </div>
      </div>
    </div>
  );
}
