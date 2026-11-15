import React from 'react';
import { History, Shield, ArrowRight, User, Terminal, Clock } from 'lucide-react';
import { MissionHistoryResponse } from '../types/mission';

interface MissionTimelineProps {
  history: MissionHistoryResponse;
}

export const MissionTimeline: React.FC<MissionTimelineProps> = ({ history }) => {
  const events = [
    ...(history.state_transitions || []).map((t) => ({
      id: t.transition_id,
      type: 'STATE_TRANSITION',
      title: `State Transition: ${t.from_state} ➔ ${t.to_state}`,
      description: t.reason,
      operator: t.operator_id,
      timestamp: t.timestamp,
      version: t.context_version,
      evidence: t.evidence
    })),
    ...(history.audit_events || []).map((a) => ({
      id: a.event_id,
      type: a.event_type,
      title: a.event_type.replace(/_/g, ' '),
      description: a.description,
      operator: a.operator_id,
      timestamp: a.timestamp,
      version: a.context_version,
      evidence: a.evidence
    }))
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div className="flex items-center space-x-2">
          <History className="h-5 w-5 text-amber-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section G • Mission Audit Timeline & Historical Trace
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Persistent SQLite Ledger ({events.length} Entries)
        </span>
      </div>

      <div className="mt-4 max-h-72 overflow-y-auto space-y-3 pr-1">
        {events.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-500 font-mono">
            No historical transitions recorded in database yet.
          </div>
        ) : (
          events.map((ev) => (
            <div
              key={ev.id}
              className="p-3 rounded-lg bg-[#060913] border border-[#1E293B] text-xs font-mono transition hover:border-slate-700"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px] text-slate-500">
                <div className="flex items-center space-x-2">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold text-[10px]">
                    v{ev.version}
                  </span>
                  <span className="font-bold text-slate-200 uppercase">{ev.title}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="flex items-center space-x-1">
                    <User className="h-3 w-3 text-slate-500" />
                    <span>{ev.operator}</span>
                  </span>
                  <span className="text-slate-400">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
              <p className="mt-1 text-slate-300 font-sans text-xs">
                {ev.description}
              </p>
              {ev.evidence && Object.keys(ev.evidence).length > 0 && (
                <div className="mt-2 text-[10px] text-slate-500 font-mono bg-slate-950 p-1.5 rounded truncate">
                  Evidence: {JSON.stringify(ev.evidence)}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

