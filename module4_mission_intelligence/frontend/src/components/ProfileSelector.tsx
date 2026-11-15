import React from 'react';
import { Rocket, CheckCircle2, ChevronRight, Globe2 } from 'lucide-react';
import { MissionProfile } from '../types/mission';

interface ProfileSelectorProps {
  profiles: MissionProfile[];
  activeMissionId: string;
  onSelectMission: (missionId: string) => void;
  isLoading: boolean;
}

export const ProfileSelector: React.FC<ProfileSelectorProps> = ({
  profiles,
  activeMissionId,
  onSelectMission,
  isLoading
}) => {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between pb-4 border-b border-[#1E293B]">
        <div className="flex items-center space-x-2">
          <Rocket className="h-5 w-5 text-amber-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section H • Mission Profile Configuration Templates
          </h2>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Dynamic Template Engine (Preserves History)
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {profiles.map((p) => {
          const isActive = p.mission_id === activeMissionId;
          return (
            <div
              key={p.mission_id}
              onClick={() => !isActive && !isLoading && onSelectMission(p.mission_id)}
              className={`p-4 rounded-xl border transition cursor-pointer flex flex-col justify-between ${
                isActive
                  ? 'bg-amber-950/20 border-amber-500/80 shadow-lg shadow-amber-950/30 ring-1 ring-amber-500'
                  : 'bg-[#060913] border-[#1E293B] hover:border-slate-600 hover:bg-slate-900/40'
              }`}
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-amber-400">
                    {p.destination}
                  </span>
                  {isActive && (
                    <span className="flex items-center space-x-1 text-[11px] font-mono font-bold text-emerald-400">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>ACTIVE</span>
                    </span>
                  )}
                </div>

                <h3 className="text-sm font-bold text-slate-100 mt-1 line-clamp-1">
                  {p.mission_name}
                </h3>

                <div className="space-y-1 mt-3 text-xs font-mono text-slate-400">
                  <div className="flex justify-between">
                    <span>Gravity:</span>
                    <span className="text-slate-200 font-semibold">{p.gravity_environment} ({p.gravity_value_g.toFixed(3)}g)</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Latency:</span>
                    <span className="text-slate-200">{p.communication_characteristics.expected_delay_seconds}s one-way</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Duration:</span>
                    <span className="text-slate-200">{p.expected_duration_days || 'UNSPECIFIED'} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Habitat:</span>
                    <span className="text-slate-200 truncate max-w-[130px]">{p.habitat_type}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs font-mono">
                <span className="text-slate-500">v{p.configuration_version}</span>
                <button
                  disabled={isActive || isLoading}
                  className={`px-2.5 py-1 rounded text-[11px] font-bold transition ${
                    isActive
                      ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-600/30'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  {isActive ? 'Engaged' : 'Select Mission'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

