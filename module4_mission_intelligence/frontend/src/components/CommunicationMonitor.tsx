import React from 'react';
import { Radio, Signal, Clock, Send, CheckCheck, AlertOctagon, Database } from 'lucide-react';
import { CommunicationContext } from '../types/mission';

interface CommunicationMonitorProps {
  communication: CommunicationContext;
}

export const CommunicationMonitor: React.FC<CommunicationMonitorProps> = ({ communication }) => {
  const isBlackout = communication.status === 'BLACKOUT';
  const oneWayDelay = communication.expected_delay_seconds;
  const roundTripDelay = oneWayDelay * 2;

  const pipelineStages = [
    {
      id: 'LOCALLY_GENERATED',
      label: 'Locally Generated',
      desc: 'Captured and cryptographically logged in onboard spacecraft SQLite buffer.',
      icon: Database,
      active: true
    },
    {
      id: 'QUEUED',
      label: 'Queued in Uplink Buffer',
      desc: 'Buffered awaiting DSN / high-gain steerable antenna pointing window.',
      icon: Clock,
      active: communication.queued_reports_count > 0 || !isBlackout
    },
    {
      id: 'TRANSMITTED',
      label: 'Transmitted into Deep Space',
      desc: `Propagating via RF at light speed. Round-trip light time: ~${roundTripDelay >= 60 ? (roundTripDelay / 60).toFixed(1) + ' min' : roundTripDelay.toFixed(0) + 's'}.`,
      icon: Send,
      active: communication.earth_reachable && !isBlackout
    },
    {
      id: 'ACKNOWLEDGED',
      label: 'Earth Acknowledged',
      desc: 'Explicit telemetry handshake confirmed by Mission Control Ground Station.',
      icon: CheckCheck,
      active: communication.last_acknowledged_timestamp !== null && !isBlackout
    }
  ];

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div className="flex items-center space-x-2">
          <Signal className={`h-5 w-5 ${isBlackout ? 'text-crimson-400' : 'text-cyan-400'}`} />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section F • Communication & Local-First Autonomy Constraints
          </h2>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className={`px-2 py-0.5 rounded font-bold border ${
            isBlackout
              ? 'bg-crimson-950/80 text-crimson-400 border-crimson-500 animate-pulse'
              : 'bg-emerald-950/60 text-emerald-400 border-emerald-600/40'
          }`}>
            LINK: {communication.status}
          </span>
        </div>
      </div>

      {/* Latency and Reachability Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
        <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
          <span className="text-[10px] font-mono uppercase text-slate-500">ONE-WAY LATENCY</span>
          <div className="text-sm font-bold font-mono text-slate-200 mt-0.5">
            {oneWayDelay >= 60 ? `${(oneWayDelay / 60).toFixed(1)} min` : `${oneWayDelay.toFixed(1)} sec`}
          </div>
          <span className="text-[10px] font-mono text-slate-500">{oneWayDelay.toFixed(1)}s light-time</span>
        </div>

        <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
          <span className="text-[10px] font-mono uppercase text-slate-500">ROUND-TRIP DECISION WINDOW</span>
          <div className="text-sm font-bold font-mono text-amber-400 mt-0.5">
            {roundTripDelay >= 60 ? `${(roundTripDelay / 60).toFixed(1)} min` : `${roundTripDelay.toFixed(1)} sec`}
          </div>
          <span className="text-[10px] font-mono text-slate-500">Local autonomy mandatory</span>
        </div>

        <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
          <span className="text-[10px] font-mono uppercase text-slate-500">EARTH REACHABILITY</span>
          <div className={`text-sm font-bold font-mono mt-0.5 ${communication.earth_reachable ? 'text-emerald-400' : 'text-crimson-400'}`}>
            {communication.earth_reachable ? 'GROUND STATION VISIBLE' : 'LINE-OF-SIGHT LOST'}
          </div>
          <span className="text-[10px] font-mono text-slate-500">Deep Space Network</span>
        </div>

        <div className="bg-[#060913] p-3 rounded-lg border border-[#1E293B]">
          <span className="text-[10px] font-mono uppercase text-slate-500">BUFFERED QUEUE</span>
          <div className="text-sm font-bold font-mono text-slate-200 mt-0.5">
            {communication.queued_reports_count} reports
          </div>
          <span className="text-[10px] font-mono text-slate-500">Delayed-tolerant delivery</span>
        </div>
      </div>

      {/* Local-First Delivery Pipeline Visualization */}
      <div className="mt-5 pt-4 border-t border-[#1E293B]">
        <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-3">
          Deep-Space Delivery Pipeline State (Never claims Earth delivery without verified ACK)
        </span>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          {pipelineStages.map((stage, idx) => {
            const Icon = stage.icon;
            return (
              <div
                key={stage.id}
                className={`p-3 rounded-lg border font-mono transition ${
                  stage.active
                    ? 'bg-[#060913] border-cyan-500/40 text-slate-200'
                    : 'bg-[#060913]/40 border-[#1E293B] text-slate-600'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Icon className={`h-4 w-4 ${stage.active ? 'text-cyan-400' : 'text-slate-600'}`} />
                  <span className="text-xs font-bold uppercase">{stage.label}</span>
                </div>
                <p className="text-[11px] font-sans mt-1.5 text-slate-400 leading-tight">
                  {stage.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

