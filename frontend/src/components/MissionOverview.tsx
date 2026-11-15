import React from 'react';
import { Compass, Navigation, Globe, Layers, AlertCircle, ShieldCheck } from 'lucide-react';
import { MissionContextResponse, MissionProfile } from '../types/mission';

interface MissionOverviewProps {
  context: MissionContextResponse;
  profile?: MissionProfile;
}

export const MissionOverview: React.FC<MissionOverviewProps> = ({ context, profile }) => {
  const isPhaseDivergent = profile && profile.mission_phase.toUpperCase() !== context.actual_mission_phase.toUpperCase();

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#1E293B] gap-2">
        <div className="flex items-center space-x-2">
          <Compass className="h-5 w-5 text-crimson-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section A • Mission Overview
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-amber-950/60 text-amber-400 border border-amber-500/40">
            SOURCE: {context.data_source}
          </span>
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-slate-800 text-slate-300 border border-slate-700">
            ID: {context.mission_id}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
        {/* Destination */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <Globe className="h-3.5 w-3.5 text-slate-500" />
            <span>Destination</span>
          </div>
          <div className="mt-1 text-sm font-bold text-[#F8FAFC]">
            {profile?.destination || 'DEEP_SPACE'}
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-0.5 truncate">
            {profile?.habitat_type || 'MODULAR_HAB'}
          </div>
        </div>

        {/* Planned Mission Phase */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <Navigation className="h-3.5 w-3.5 text-slate-500" />
            <span>Planned Phase</span>
          </div>
          <div className="mt-1 text-xs font-mono font-semibold text-slate-300 truncate" title={profile?.mission_phase}>
            {profile?.mission_phase || 'UNKNOWN'}
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-0.5">
            Baseline Profile
          </div>
        </div>

        {/* Actual Verified Phase */}
        <div className={`p-3.5 rounded-lg border ${isPhaseDivergent ? 'bg-amber-950/30 border-amber-500/50' : 'bg-[#060913] border-[#1E293B]'}`}>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <Compass className={`h-3.5 w-3.5 ${isPhaseDivergent ? 'text-amber-400' : 'text-slate-500'}`} />
              <span>Actual Phase</span>
            </div>
            {isPhaseDivergent && (
              <span className="text-[10px] text-amber-400 font-mono font-bold animate-pulse">DEVIATION</span>
            )}
          </div>
          <div className={`mt-1 text-xs font-mono font-bold truncate ${isPhaseDivergent ? 'text-amber-300' : 'text-emerald-400'}`} title={context.actual_mission_phase}>
            {context.actual_mission_phase}
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-0.5">
            Verified Trajectory
          </div>
        </div>

        {/* Context Version & Freshness */}
        <div className="bg-[#060913] p-3.5 rounded-lg border border-[#1E293B]">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider flex items-center space-x-1.5">
            <Layers className="h-3.5 w-3.5 text-slate-500" />
            <span>Context Version</span>
          </div>
          <div className="mt-1 text-sm font-bold text-cyan-400 font-mono">
            v{context.context_version} <span className="text-xs text-slate-500 font-normal">({context.context_id})</span>
          </div>
          <div className="text-[11px] text-slate-500 font-mono mt-0.5">
            Quality: {context.data_quality.overall_status}
          </div>
        </div>
      </div>
    </div>
  );
};

