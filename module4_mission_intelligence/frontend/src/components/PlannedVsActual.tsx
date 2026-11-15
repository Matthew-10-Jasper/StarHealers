import React from 'react';
import { ArrowRight, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';
import { MissionContextResponse, MissionProfile } from '../types/mission';

interface PlannedVsActualProps {
  context: MissionContextResponse;
  profile?: MissionProfile;
}

export const PlannedVsActual: React.FC<PlannedVsActualProps> = ({ context, profile }) => {
  if (!profile) return null;

  const comparisons = [
    {
      category: 'Mission Phase',
      planned: profile.mission_phase,
      actual: context.actual_mission_phase,
      isMismatch: profile.mission_phase.toUpperCase() !== context.actual_mission_phase.toUpperCase(),
      severity: 'WARNING'
    },
    {
      category: 'Gravity Environment',
      planned: `${profile.gravity_environment} (${profile.gravity_value_g.toFixed(3)}g)`,
      actual: `${context.gravity_environment} (${context.gravity_value_g.toFixed(3)}g)`,
      isMismatch: profile.gravity_environment !== context.gravity_environment,
      severity: 'CRITICAL'
    },
    {
      category: 'Communication Link',
      planned: `Nominal Delay ~${profile.communication_characteristics.expected_delay_seconds.toFixed(1)}s`,
      actual: `Status: ${context.communication.status} (Latency: ${context.communication.expected_delay_seconds.toFixed(1)}s)`,
      isMismatch: context.communication.status === 'BLACKOUT' || context.communication.status === 'DEGRADED',
      severity: context.communication.status === 'BLACKOUT' ? 'CRITICAL' : 'WARNING'
    },
    {
      category: 'Radiation Environment',
      planned: 'Nominal Background Cosmic Flux',
      actual: context.environment.radiation_status,
      isMismatch: context.environment.radiation_status.includes('CRITICAL') || context.environment.radiation_status.includes('ELEVATED'),
      severity: context.environment.radiation_status.includes('CRITICAL') ? 'CRITICAL' : 'WARNING'
    },
    {
      category: 'Life-Support (ECLSS)',
      planned: 'Dual Active Closed-Loop Scrubber',
      actual: context.environment.life_support_status,
      isMismatch: context.environment.life_support_status !== 'NOMINAL' && context.environment.life_support_status !== 'UNKNOWN',
      severity: context.environment.life_support_status === 'CRITICAL' ? 'CRITICAL' : 'WARNING'
    },
    {
      category: 'Habitat Structure',
      planned: profile.habitat_type,
      actual: context.environment.habitat_status,
      isMismatch: context.environment.habitat_status !== 'NOMINAL' && context.environment.habitat_status !== 'UNKNOWN',
      severity: context.environment.habitat_status.includes('BREACH') ? 'CRITICAL' : 'WARNING'
    }
  ];

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
          Section B • Planned vs. Actual Environment Matrix
        </h2>
        <span className="text-xs text-slate-400 font-mono">
          Differential Intelligence Engine
        </span>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-[#1E293B] text-slate-400 text-[11px] uppercase">
              <th className="py-2.5 px-3">Environmental Parameter</th>
              <th className="py-2.5 px-3">Planned Baseline</th>
              <th className="py-2.5 px-2 text-center">Vector</th>
              <th className="py-2.5 px-3">Actual Verified Observation</th>
              <th className="py-2.5 px-3 text-right">Differential Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E293B]/60">
            {comparisons.map((row, idx) => {
              const isUnknown = row.actual === 'UNKNOWN';
              return (
                <tr
                  key={idx}
                  className={`transition hover:bg-slate-800/40 ${
                    row.isMismatch
                      ? row.severity === 'CRITICAL'
                        ? 'bg-crimson-950/20'
                        : 'bg-amber-950/20'
                      : ''
                  }`}
                >
                  <td className="py-3 px-3 font-medium text-slate-200">
                    {row.category}
                  </td>
                  <td className="py-3 px-3 text-slate-400 truncate max-w-xs">
                    {row.planned}
                  </td>
                  <td className="py-3 px-2 text-center text-slate-600">
                    <ArrowRight className="h-3 w-3 inline" />
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-200 truncate max-w-xs">
                    {row.actual}
                  </td>
                  <td className="py-3 px-3 text-right">
                    {isUnknown ? (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700">
                        <HelpCircle className="h-3 w-3 text-slate-400" />
                        <span>UNKNOWN</span>
                      </span>
                    ) : row.isMismatch ? (
                      <span
                        className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold border ${
                          row.severity === 'CRITICAL'
                            ? 'bg-crimson-950/60 text-crimson-400 border-crimson-500/50'
                            : 'bg-amber-950/60 text-amber-400 border-amber-500/50'
                        }`}
                      >
                        <AlertTriangle className="h-3 w-3" />
                        <span>{row.severity} DEVIATION</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] bg-emerald-950/40 text-emerald-400 border border-emerald-600/30">
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                        <span>ALIGNED</span>
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

