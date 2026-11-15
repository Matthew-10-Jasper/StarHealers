import React from 'react';
import Modal from '../../common/Modal';
import SeverityBadge from '../../common/SeverityBadge';
import {
  ShieldAlert,
  AlertTriangle,
  Clock,
  User,
  CheckCircle,
  FileText,
  ListOrdered,
  Info,
  CheckCircle2,
} from 'lucide-react';

export default function AlertDetailModal({
  isOpen,
  onClose,
  alert,
  astronaut,
  onAcknowledge,
}) {
  if (!alert) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={alert.title}
      subtitle={`Alert ID: ${alert.id} | Rule: ${alert.ruleId || 'N/A'}`}
      maxWidth="max-w-3xl"
    >
      <div className="space-y-6">
        {/* Header Overview Card */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="text-[10px] font-mono text-slate-400 block mb-1">AFFECTED ASTRONAUT</span>
            <div className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs font-semibold text-white">{astronaut?.name || alert.astronautId}</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">{alert.astronautId}</span>
          </div>

          <div>
            <span className="text-[10px] font-mono text-slate-400 block mb-1">ALERT SEVERITY</span>
            <SeverityBadge severity={alert.severity} size="md" />
          </div>

          <div>
            <span className="text-[10px] font-mono text-slate-400 block mb-1">TRIGGER TIMESTAMP</span>
            <div className="flex items-center gap-1 text-xs font-mono text-slate-300">
              <Clock className="w-3 h-3 text-slate-500" />
              <span>{alert.timestamp ? alert.timestamp.replace('T', ' ').substring(0, 19) + ' UTC' : '—'}</span>
            </div>
          </div>

          <div>
            <span className="text-[10px] font-mono text-slate-400 block mb-1">CURRENT STATUS</span>
            <span
              className={`inline-flex items-center gap-1 text-xs font-mono font-semibold px-2 py-0.5 rounded border ${
                alert.status === 'ACTIVE'
                  ? 'bg-rose-950/60 border-rose-500/50 text-rose-300'
                  : 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
              }`}
            >
              {alert.status === 'ACTIVE' ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                  ACTIVE
                </>
              ) : (
                <>
                  <CheckCircle className="w-3 h-3 text-emerald-400" />
                  RESOLVED
                </>
              )}
            </span>
          </div>
        </div>

        {/* Transparent Medical Evidence / Trigger Reason */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 font-semibold">
            <FileText className="w-4 h-4" />
            <span>EXPLAINABLE RULE REASONING</span>
          </div>
          <p className="text-xs text-slate-200 leading-relaxed font-sans">
            {alert.explanation}
          </p>
          <div className="pt-2 text-[11px] font-mono text-slate-400 border-t border-slate-800">
            <strong>TRIGGER CRITERIA:</strong> {alert.triggerReason}
          </div>
        </div>

        {/* Contributing Measurements Breakdown */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
              CONTRIBUTING PHYSIOLOGICAL MEASUREMENTS
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Evaluated against configured medical thresholds
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 text-[10px] uppercase">
                <tr>
                  <th className="py-2.5 px-3">Metric Name</th>
                  <th className="py-2.5 px-3">Recorded Value</th>
                  <th className="py-2.5 px-3">Configured Threshold</th>
                  <th className="py-2.5 px-3">Variance Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 bg-slate-950/40">
                {alert.contributingMeasurements?.map((m, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/50">
                    <td className="py-2.5 px-3 text-slate-200 font-semibold font-sans">{m.name}</td>
                    <td className="py-2.5 px-3 font-bold text-white">{m.value}</td>
                    <td className="py-2.5 px-3 text-slate-400">{m.threshold}</td>
                    <td className="py-2.5 px-3">
                      <SeverityBadge severity={m.status || alert.severity} size="sm" showIcon={false} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recommended Clinical Countermeasures & Escalation Protocol */}
        {alert.escalationSteps && alert.escalationSteps.length > 0 && (
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-xs font-mono text-amber-400 font-semibold">
              <ListOrdered className="w-4 h-4" />
              <span>RECOMMENDED ESCALATION PROTOCOL (NASA FLIGHT RULE COMPLIANT)</span>
            </div>
            <ul className="space-y-2">
              {alert.escalationSteps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                  <span className="flex items-center justify-center w-4 h-4 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-mono text-cyan-400 shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Controls & Acknowledgement */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800">
          <div className="text-[11px] font-mono text-slate-400">
            {alert.acknowledgedBy ? (
              <span className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" /> Acknowledged by {alert.acknowledgedBy}
              </span>
            ) : (
              <span className="text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> Pending Medical Officer review
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {alert.status === 'ACTIVE' && (
              <button
                onClick={() => {
                  onAcknowledge && onAcknowledge(alert.id);
                  onClose();
                }}
                className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold transition shadow-cyan-glow"
              >
                Mark as Acknowledged / Resolved
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs transition"
            >
              Close
            </button>
          </div>
        </div>

        {/* Medical Safety Disclaimer */}
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-400 flex items-start gap-2">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <p>
            CLINICAL SAFETY DISCLAIMER: Rule-based triage algorithms provide real-time decision support for crew safety and autonomous mission operation. These thresholds require validation against authoritative aerospace medical guidelines and do not replace formal clinical assessment.
          </p>
        </div>
      </div>
    </Modal>
  );
}
