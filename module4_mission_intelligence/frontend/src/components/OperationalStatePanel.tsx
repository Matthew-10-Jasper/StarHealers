import React, { useState } from 'react';
import { ShieldAlert, ArrowRightCircle, Check, AlertOctagon, HelpCircle, Activity } from 'lucide-react';
import { OperationalState } from '../types/mission';

interface OperationalStatePanelProps {
  currentState: OperationalState;
  onTransition: (targetState: OperationalState, reason: string, evidence?: Record<string, any>) => Promise<void>;
  isLoading: boolean;
}

export const OperationalStatePanel: React.FC<OperationalStatePanelProps> = ({
  currentState,
  onTransition,
  isLoading
}) => {
  const [targetState, setTargetState] = useState<OperationalState>('DEGRADED');
  const [reason, setReason] = useState('');
  const [evidenceNotes, setEvidenceNotes] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const states: { state: OperationalState; label: string; desc: string; color: string }[] = [
    {
      state: 'NOMINAL',
      label: 'NOMINAL',
      desc: 'All mission systems and environmental bounds fully aligned with flight plan.',
      color: 'border-emerald-500/50 bg-emerald-950/20 text-emerald-400'
    },
    {
      state: 'DEGRADED',
      label: 'DEGRADED',
      desc: 'Non-critical subsystem impairment or warning-level environmental divergence.',
      color: 'border-amber-500/50 bg-amber-950/20 text-amber-400'
    },
    {
      state: 'CONTINGENCY',
      label: 'CONTINGENCY',
      desc: 'Active critical mission hazard, life-support failure, or structural compromise.',
      color: 'border-crimson-500/80 bg-crimson-950/30 text-crimson-400'
    },
    {
      state: 'RECOVERY',
      label: 'RECOVERY',
      desc: 'Active crew or automated stabilization protocol under verification before nominal.',
      color: 'border-cyan-500/50 bg-cyan-950/20 text-cyan-400'
    },
    {
      state: 'UNKNOWN',
      label: 'UNKNOWN',
      desc: 'Environmental state cannot be reliably determined due to telemetry loss.',
      color: 'border-slate-500/50 bg-slate-900/40 text-slate-300'
    }
  ];

  const handleExecuteTransition = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if (!reason.trim()) {
      setErrorMsg('A validated operational reason is required for state transitions.');
      return;
    }

    try {
      await onTransition(targetState, reason, {
        operator_notes: evidenceNotes,
        verification_passed: true,
        sensor_check: 'MANUAL_OVERRIDE_VERIFIED'
      });
      setReason('');
      setEvidenceNotes('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Transition rejected by Contingency State Manager');
    }
  };

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-amber-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section C • Operational State & Contingency Manager
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Deterministic 5-State Transition Engine
        </span>
      </div>

      {/* Five States Visual Display */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 mt-4">
        {states.map((s) => {
          const isActive = s.state === currentState;
          return (
            <div
              key={s.state}
              className={`p-3.5 rounded-lg border transition relative ${
                isActive
                  ? `${s.color} ring-2 ring-offset-2 ring-offset-[#060913] ${
                      s.state === 'CONTINGENCY' ? 'ring-crimson-500' : 'ring-amber-500'
                    }`
                  : 'bg-[#060913] border-[#1E293B] text-slate-500 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold tracking-wider">
                  {s.label}
                </span>
                {isActive && (
                  <span className="h-2 w-2 rounded-full bg-current animate-ping" />
                )}
              </div>
              <p className="text-[11px] font-sans mt-2 leading-relaxed line-clamp-3">
                {s.desc}
              </p>
              {isActive && (
                <div className="mt-2 text-[10px] font-mono uppercase font-bold tracking-widest text-white/90">
                  ● ACTIVE STATE
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Controlled State Transition Form */}
      <div className="mt-6 pt-5 border-t border-[#1E293B] bg-[#060913]/60 p-4 rounded-lg border border-[#1E293B]">
        <h3 className="text-xs font-mono text-slate-300 font-bold uppercase tracking-wider mb-3 flex items-center space-x-2">
          <ArrowRightCircle className="h-4 w-4 text-amber-400" />
          <span>Execute Controlled State Transition (Flight Director Authorization)</span>
        </h3>

        {errorMsg && (
          <div className="mb-3 p-2.5 rounded bg-crimson-950/60 border border-crimson-500/50 text-crimson-300 text-xs font-mono">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleExecuteTransition} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
          <div className="md:col-span-3">
            <label className="block text-[11px] font-mono text-slate-400 mb-1">
              TARGET STATE
            </label>
            <select
              value={targetState}
              onChange={(e) => setTargetState(e.target.value as OperationalState)}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded px-3 py-1.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="NOMINAL">NOMINAL (Requires Verified Evidence)</option>
              <option value="DEGRADED">DEGRADED (Warning / Impairment)</option>
              <option value="CONTINGENCY">CONTINGENCY (Critical Hazard)</option>
              <option value="RECOVERY">RECOVERY (Stabilizing)</option>
              <option value="UNKNOWN">UNKNOWN (Telemetry Lost)</option>
            </select>
          </div>

          <div className="md:col-span-4">
            <label className="block text-[11px] font-mono text-slate-400 mb-1">
              OPERATIONAL REASON (MANDATORY)
            </label>
            <input
              type="text"
              placeholder="e.g. Scrubber 2 recovered, nominal delta-P"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded px-3 py-1.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div className="md:col-span-3">
            <label className="block text-[11px] font-mono text-slate-400 mb-1">
              EVIDENCE NOTES
            </label>
            <input
              type="text"
              placeholder="e.g. Telemetry sensor checks passed"
              value={evidenceNotes}
              onChange={(e) => setEvidenceNotes(e.target.value)}
              className="w-full bg-[#0F172A] border border-[#1E293B] rounded px-3 py-1.5 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-1.5 px-3 rounded bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-slate-950 font-mono text-xs font-bold transition flex items-center justify-center space-x-1.5"
            >
              <span>DISPATCH</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

