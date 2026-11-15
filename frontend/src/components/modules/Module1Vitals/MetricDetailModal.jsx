import React from 'react';
import Modal from '../../common/Modal';
import SeverityBadge from '../../common/SeverityBadge';
import DataSourceBadge from '../../common/DataSourceBadge';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { AlertCircle, CheckCircle, HelpCircle, Activity } from 'lucide-react';

export default function MetricDetailModal({
  isOpen,
  onClose,
  metricKey,
  metricDef,
  reading,
  astronaut,
  historicalData,
}) {
  if (!metricDef) return null;

  const isNoData = !reading || reading.value === null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${metricDef.label} Telemetry Analysis`}
      subtitle={`Astronaut: ${astronaut.name} (${astronaut.id}) | Node: ${metricDef.bodyRegion}`}
      maxWidth="max-w-3xl"
    >
      <div className="space-y-6">
        {/* Top Summary Banner */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-900/90 border border-slate-800">
          <div>
            <span className="text-[11px] font-mono text-slate-400 block mb-1">CURRENT READING</span>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-bold font-mono text-white">
                {isNoData ? 'NO DATA' : reading.value ?? `${reading.systolic}/${reading.diastolic}`}
              </span>
              <span className="text-xs font-mono text-cyan-400">{metricDef.unit}</span>
            </div>
          </div>

          <div>
            <span className="text-[11px] font-mono text-slate-400 block mb-1">SEVERITY STATUS</span>
            <SeverityBadge severity={reading?.status || 'NO_DATA'} size="md" />
          </div>

          <div>
            <span className="text-[11px] font-mono text-slate-400 block mb-1">REFERENCE RANGE</span>
            <span className="text-xs font-mono text-slate-200">
              {metricKey === 'bloodPressure'
                ? '90-130 / 60-85 mmHg'
                : `${metricDef.normalMin} - ${metricDef.normalMax} ${metricDef.unit}`}
            </span>
            <div className="flex items-center gap-1 text-[10px] text-cyan-400 mt-1">
              {reading?.status === 'NORMAL' ? (
                <>
                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400">Within Nominal Range</span>
                </>
              ) : reading?.status === 'WARNING' || reading?.status === 'CRITICAL' ? (
                <>
                  <AlertCircle className="w-3 h-3 text-amber-400" />
                  <span className="text-amber-400">Threshold Exceeded</span>
                </>
              ) : (
                <>
                  <HelpCircle className="w-3 h-3 text-slate-400" />
                  <span className="text-slate-400">Status Undetermined</span>
                </>
              )}
            </div>
          </div>

          <div>
            <span className="text-[11px] font-mono text-slate-400 block mb-1">DATA PROVENANCE</span>
            <DataSourceBadge source={reading?.source} quality={reading?.quality} />
            <span className="text-[10px] font-mono text-slate-400 block mt-1">
              Time: {reading?.timestamp ? reading.timestamp.replace('T', ' ').substring(0, 19) + ' UTC' : '—'}
            </span>
          </div>
        </div>

        {/* Clinical / Operational Description */}
        <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
          <span className="text-cyan-400 font-semibold font-mono mr-1">PHYSIOLOGICAL FUNCTION:</span>
          {metricDef.description}. Associated with anatomical monitoring zone <strong className="text-slate-200">{metricDef.bodyRegion}</strong>.
        </div>

        {/* Historical Chart */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-xs font-mono tracking-wider text-slate-300 uppercase flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              Trend Trajectory (24-Hour Window)
            </h4>
            <span className="text-[10px] font-mono text-slate-400">
              Unit: {metricDef.unit}
            </span>
          </div>

          <div className="h-48 w-full">
            {isNoData ? (
              <div className="h-full flex items-center justify-center text-slate-500 font-mono text-xs">
                No historical telemetry points available for this sensor node.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historicalData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="detailGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                  <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#64748B" tick={{ fontSize: 10 }} domain={['dataMin - 5', 'dataMax + 5']} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: '#334155',
                      borderRadius: '8px',
                      fontSize: '11px',
                    }}
                    labelStyle={{ color: '#94A3B8', fontFamily: 'monospace' }}
                    itemStyle={{ color: '#00F0FF', fontFamily: 'monospace' }}
                  />
                  <Area
                    type="monotone"
                    dataKey={metricKey}
                    stroke="#00F0FF"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#detailGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Medical Limitation & Evidence Notice */}
        <div className="p-3 rounded-lg bg-cyan-950/20 border border-cyan-800/30 text-[11px] text-cyan-300 font-mono">
          <p>
            NOTICE: Telemetry values represent continuous physiological monitoring for deep-space mission situational awareness. Automated alerts reflect configured clinical threshold triggers and must be cross-evaluated with crew environmental logs and flight surgeon review.
          </p>
        </div>
      </div>
    </Modal>
  );
}
