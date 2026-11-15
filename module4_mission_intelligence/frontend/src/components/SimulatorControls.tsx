import React from 'react';
import { Play, Flame, WifiOff, Wind, Compass, RefreshCw, AlertCircle, Sparkles } from 'lucide-react';

interface SimulatorControlsProps {
  onTriggerScenario: (scenario: string) => Promise<void>;
  onGenerateStream: () => Promise<void>;
  onChangePhase: (phase: string) => Promise<void>;
  isLoading: boolean;
}

export const SimulatorControls: React.FC<SimulatorControlsProps> = ({
  onTriggerScenario,
  onGenerateStream,
  onChangePhase,
  isLoading
}) => {
  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-lg relative overflow-hidden">
      {/* Top Banner Notice */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#1E293B] gap-2">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-crimson-400" />
          <h2 className="text-base font-semibold text-[#F8FAFC] tracking-tight">
            Section I • Development Telemetry Simulator
          </h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-crimson-950/80 text-crimson-400 border border-crimson-500/60 animate-pulse">
            DATA SOURCE: SIMULATED ONLY
          </span>
        </div>
      </div>

      <p className="text-xs text-slate-400 font-sans mt-2">
        Inject controlled synthetic sensor telemetry and off-nominal mission events to stress-test
        the Mission Environment Intelligence engine. Does not operate a real spacecraft.
      </p>

      {/* Simulator Scenario Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
        {/* Nominal Stream */}
        <button
          onClick={() => onGenerateStream()}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-slate-900 border border-[#1E293B] hover:border-emerald-500/50 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <Play className="h-4 w-4 text-emerald-400 group-hover:scale-110 transition" />
            <span className="text-[10px] font-mono text-emerald-400 font-bold">NOMINAL</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            Generate Stream
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Standard Telemetry
          </div>
        </button>

        {/* ECLSS Life-Support Degradation */}
        <button
          onClick={() => onTriggerScenario('LIFE_SUPPORT')}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-amber-950/20 border border-[#1E293B] hover:border-amber-500/60 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <Wind className="h-4 w-4 text-amber-400 group-hover:scale-110 transition" />
            <span className="text-[10px] font-mono text-amber-400 font-bold">WARNING</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            ECLSS Degradation
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Scrubber Bed Failure
          </div>
        </button>

        {/* Communication Loss */}
        <button
          onClick={() => onTriggerScenario('COMM_LOSS')}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-crimson-950/20 border border-[#1E293B] hover:border-crimson-500/60 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <WifiOff className="h-4 w-4 text-crimson-400 group-hover:scale-110 transition" />
            <span className="text-[10px] font-mono text-crimson-400 font-bold">CRITICAL</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            Comm Blackout
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            RF Gimbal Failure
          </div>
        </button>

        {/* Solar Radiation Event */}
        <button
          onClick={() => onTriggerScenario('RADIATION_SPIKE')}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-crimson-950/20 border border-[#1E293B] hover:border-crimson-500/60 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <Flame className="h-4 w-4 text-crimson-400 group-hover:scale-110 transition" />
            <span className="text-[10px] font-mono text-crimson-400 font-bold">CRITICAL</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            SPE Radiation Flare
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            4.8 mSv/day Spike
          </div>
        </button>

        {/* Trajectory Phase Deviation */}
        <button
          onClick={() => onChangePhase('OFF_NOMINAL_ABORT_TRAJECTORY')}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-amber-950/20 border border-[#1E293B] hover:border-amber-500/60 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <Compass className="h-4 w-4 text-amber-400 group-hover:scale-110 transition" />
            <span className="text-[10px] font-mono text-amber-400 font-bold">DEVIATION</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            Trajectory Abort
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Phase Change
          </div>
        </button>

        {/* Restore Nominal */}
        <button
          onClick={() => onTriggerScenario('RESTORE_NOMINAL')}
          disabled={isLoading}
          className="p-3 rounded-lg bg-[#060913] hover:bg-emerald-950/30 border border-[#1E293B] hover:border-emerald-500 text-left transition flex flex-col justify-between group"
        >
          <div className="flex items-center justify-between">
            <RefreshCw className="h-4 w-4 text-emerald-400 group-hover:rotate-180 transition duration-500" />
            <span className="text-[10px] font-mono text-emerald-400 font-bold">RESET</span>
          </div>
          <div className="mt-2 text-xs font-bold text-slate-200">
            Restore Nominal
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-1">
            Clear Hazards
          </div>
        </button>
      </div>
    </div>
  );
};
