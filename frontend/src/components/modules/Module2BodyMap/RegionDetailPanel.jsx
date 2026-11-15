import React from 'react';
import SeverityBadge from '../../common/SeverityBadge';
import DataSourceBadge from '../../common/DataSourceBadge';
import { METRIC_DEFINITIONS } from '../../../data/mockData';
import {
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Activity,
  ShieldAlert,
  Info,
  ExternalLink,
} from 'lucide-react';

export default function RegionDetailPanel({
  regionId,
  regionConfig,
  regionStatus,
  astronaut,
  readings,
  alerts,
  onNavigateToMetric,
}) {
  if (!regionConfig) {
    return (
      <div className="glass-panel rounded-xl p-6 border border-slate-800 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
        <Activity className="w-10 h-10 text-slate-600 mb-3" />
        <h4 className="text-sm font-semibold text-slate-300">Select an Anatomical System</h4>
        <p className="text-xs text-slate-500 max-w-xs mt-1">
          Click on any body region on the interactive anatomical model to inspect its real-time telemetry, related physiological metrics, and active triage alerts.
        </p>
      </div>
    );
  }

  // Filter alerts related to this body region or its metrics
  const relatedAlerts = (alerts || []).filter((alert) => {
    if (alert.astronautId !== astronaut.id) return false;
    return alert.contributingMeasurements?.some((m) => {
      const metricKey = Object.keys(METRIC_DEFINITIONS).find(
        (k) => METRIC_DEFINITIONS[k].label.toLowerCase() === m.name.toLowerCase() ||
               METRIC_DEFINITIONS[k].bodyRegion.toLowerCase().includes(regionConfig.label.toLowerCase())
      );
      return regionConfig.associatedMetrics.includes(metricKey);
    });
  });

  return (
    <div className="glass-panel rounded-xl p-5 border border-slate-800 space-y-5 animate-in fade-in duration-200">
      {/* Region Header */}
      <div className="flex items-start justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-100 font-sans tracking-wide">
              {regionConfig.label}
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {regionId.toUpperCase()}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{regionConfig.description}</p>
        </div>
        <SeverityBadge severity={regionStatus || 'NO_DATA'} size="md" />
      </div>

      {/* Anatomical Subsystems */}
      <div>
        <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase block mb-1.5">
          MONITORED SUBSYSTEMS
        </span>
        <div className="flex flex-wrap gap-1.5">
          {regionConfig.subsystems.map((sub, idx) => (
            <span
              key={idx}
              className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300"
            >
              {sub}
            </span>
          ))}
        </div>
      </div>

      {/* Associated Measurements Cards */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
            ASSOCIATED BIOMETRICS
          </span>
          <span className="text-[10px] font-mono text-cyan-400">
            {regionConfig.associatedMetrics.length} Metric{regionConfig.associatedMetrics.length > 1 ? 's' : ''} Configured
          </span>
        </div>

        <div className="space-y-2">
          {regionConfig.associatedMetrics.map((metricKey) => {
            const def = METRIC_DEFINITIONS[metricKey];
            const reading = readings?.[metricKey];
            const isNoData = !reading || reading.value === null;

            return (
              <div
                key={metricKey}
                onClick={() => onNavigateToMetric && onNavigateToMetric(metricKey)}
                className="p-3 rounded-lg bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 transition cursor-pointer flex items-center justify-between group"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition">
                      {def?.label || metricKey}
                    </span>
                    <SeverityBadge severity={reading?.status || 'NO_DATA'} size="sm" showIcon={false} />
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <DataSourceBadge source={reading?.source} quality={reading?.quality} />
                    <span className="text-[10px] font-mono text-slate-400">
                      Ref: {def?.normalMin ?? '—'} - {def?.normalMax ?? '—'} {def?.unit}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-base font-bold font-mono text-white">
                    {isNoData
                      ? 'NO DATA'
                      : metricKey === 'bloodPressure'
                      ? `${reading.systolic}/${reading.diastolic}`
                      : reading.value}
                    <span className="text-xs font-mono text-cyan-400/80 ml-1">
                      {isNoData ? '' : def?.unit}
                    </span>
                  </div>
                  <span className="text-[10px] text-cyan-400 font-mono flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition">
                    Analyze <ExternalLink className="w-2.5 h-2.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Related Triage Alerts */}
      <div>
        <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase block mb-2">
          ACTIVE TRIAGE ALERTS FOR THIS REGION
        </span>

        {relatedAlerts.length > 0 ? (
          <div className="space-y-2">
            {relatedAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border text-xs ${
                  alert.severity === 'CRITICAL'
                    ? 'bg-rose-950/30 border-rose-600/40 text-rose-200'
                    : 'bg-amber-950/30 border-amber-600/40 text-amber-200'
                }`}
              >
                <div className="flex items-center justify-between font-mono font-semibold mb-1">
                  <span className="flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    {alert.title}
                  </span>
                  <span className="text-[10px] opacity-80">{alert.id}</span>
                </div>
                <p className="text-[11px] opacity-90 leading-relaxed font-sans">{alert.triggerReason}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800/80 text-xs text-slate-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>No active warning or critical triage alerts currently assigned to this system.</span>
          </div>
        )}
      </div>

      {/* Mandatory Medical Limitation Disclaimer */}
      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-400 space-y-1">
        <div className="flex items-center gap-1.5 text-cyan-400 font-semibold">
          <Info className="w-3.5 h-3.5 shrink-0" />
          <span>EVIDENCE-BASED MONITORING DISCLAIMER</span>
        </div>
        <p className="leading-normal">{regionConfig.disclaimer}</p>
      </div>
    </div>
  );
}
