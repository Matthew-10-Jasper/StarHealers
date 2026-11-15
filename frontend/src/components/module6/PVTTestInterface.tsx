import React, { useState, useEffect, useRef, useCallback } from 'react';
import { apiM6, PVTTrial, PVTSession } from '../../services/modulesApi';
import { Play, CheckCircle2, AlertTriangle, RefreshCw, Zap } from 'lucide-react';

interface PVTTestProps {
  astronautId: string;
  onSessionComplete: (session: PVTSession) => void;
}

type TestState = 'IDLE' | 'WAITING' | 'STIMULUS' | 'FEEDBACK' | 'SUBMITTING' | 'DONE';

export const PVTTestInterface: React.FC<PVTTestProps> = ({ astronautId, onSessionComplete }) => {
  const [testState, setTestState] = useState<TestState>('IDLE');
  const [currentTrial, setCurrentTrial] = useState(1);
  const totalTrials = 5;
  const [trials, setTrials] = useState<PVTTrial[]>([]);
  const [reactionTime, setReactionTime] = useState<number | null>(null);
  const [feedbackMsg, setFeedbackMsg] = useState<string>('');
  const [lastSession, setLastSession] = useState<PVTSession | null>(null);

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const startTimeRef = useRef<number>(0);
  const stimulusDelayRef = useRef<number>(0);

  const cleanupTimer = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const startNextTrial = useCallback((trialNum: number) => {
    cleanupTimer();
    setReactionTime(null);
    setFeedbackMsg('');
    setTestState('WAITING');

    // Randomized delay between 2000ms and 5000ms
    const delay = Math.floor(Math.random() * 3000) + 2000;
    stimulusDelayRef.current = delay;

    timerRef.current = setTimeout(() => {
      startTimeRef.current = performance.now();
      setTestState('STIMULUS');
    }, delay);
  }, []);

  const handleStartTest = () => {
    setTrials([]);
    setCurrentTrial(1);
    setLastSession(null);
    startNextTrial(1);
  };

  const submitSession = async (recordedTrials: PVTTrial[]) => {
    setTestState('SUBMITTING');
    try {
      const res = await apiM6.submitPVT({
        astronaut_id: astronautId,
        trials: recordedTrials.map(t => ({
          trial_number: t.trial_number,
          stimulus_delay_ms: t.stimulus_delay_ms,
          reaction_time_ms: t.reaction_time_ms
        }))
      });
      setLastSession(res);
      setTestState('DONE');
      onSessionComplete(res);
    } catch (err) {
      console.error('Failed to submit PVT session', err);
      setTestState('DONE');
    }
  };

  const handleUserTrigger = () => {
    if (testState === 'WAITING') {
      // False start!
      cleanupTimer();
      setFeedbackMsg('FALSE START (< 100ms)! Clicked prematurely.');
      const recorded: PVTTrial = {
        trial_number: currentTrial,
        stimulus_delay_ms: stimulusDelayRef.current,
        reaction_time_ms: 50.0,
        is_false_start: true,
        is_lapse: false
      };
      const updatedTrials = [...trials, recorded];
      setTrials(updatedTrials);
      setTestState('FEEDBACK');

      setTimeout(() => {
        if (currentTrial < totalTrials) {
          setCurrentTrial(prev => prev + 1);
          startNextTrial(currentTrial + 1);
        } else {
          submitSession(updatedTrials);
        }
      }, 1500);
    } else if (testState === 'STIMULUS') {
      const rt = Math.round(performance.now() - startTimeRef.current);
      setReactionTime(rt);
      const isLapse = rt > 500;
      setFeedbackMsg(isLapse ? `LAPSE DETECTED: ${rt} ms (>500ms)` : `${rt} ms`);

      const recorded: PVTTrial = {
        trial_number: currentTrial,
        stimulus_delay_ms: stimulusDelayRef.current,
        reaction_time_ms: rt,
        is_lapse: isLapse,
        is_false_start: false
      };
      const updatedTrials = [...trials, recorded];
      setTrials(updatedTrials);
      setTestState('FEEDBACK');

      setTimeout(() => {
        if (currentTrial < totalTrials) {
          setCurrentTrial(prev => prev + 1);
          startNextTrial(currentTrial + 1);
        } else {
          submitSession(updatedTrials);
        }
      }, 1200);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault();
        handleUserTrigger();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      cleanupTimer();
    };
  }, [testState, currentTrial, trials]);

  return (
    <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-5 shadow-xl relative overflow-hidden">
      <div className="flex items-center justify-between pb-3 border-b border-[#1E293B]/80 mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-indigo-500/20 text-[#6366F1]">
            <Zap className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-mono text-sm font-bold tracking-wide text-white uppercase">
              Psychomotor Vigilance Test (PVT) Interface
            </h3>
            <p className="text-xs text-slate-400">
              High-frequency behavioral alertness & reaction-time battery (5 Trials)
            </p>
          </div>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-[#1E293B] text-sky-400 border border-sky-500/30">
          Target: {astronautId}
        </span>
      </div>

      {testState === 'IDLE' && (
        <div className="py-8 text-center space-y-4">
          <p className="text-xs text-slate-300 max-w-md mx-auto">
            Click START to initiate the 5-trial psychomotor assessment. When the target area flashes{' '}
            <span className="text-[#38BDF8] font-bold">SKY CYAN</span>, press{' '}
            <kbd className="px-2 py-0.5 bg-[#1E293B] border border-slate-700 rounded text-sky-300 text-xs">
              SPACE
            </kbd>{' '}
            or click the target area as fast as possible.
          </p>
          <button
            onClick={handleStartTest}
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-[#6366F1] to-[#38BDF8] text-white font-mono text-xs font-bold tracking-wider hover:opacity-90 transition-opacity shadow-lg"
          >
            <Play className="h-4 w-4" />
            <span>START PVT TEST (5 TRIALS)</span>
          </button>
        </div>
      )}

      {(testState === 'WAITING' || testState === 'STIMULUS' || testState === 'FEEDBACK') && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400">
            <span>Trial: <strong className="text-white">{currentTrial}</strong> / {totalTrials}</span>
            <span>Trigger: <strong className="text-sky-400">SPACE</strong> or Click</span>
          </div>

          <div
            onClick={handleUserTrigger}
            className={`h-40 rounded-xl flex flex-col items-center justify-center cursor-pointer select-none transition-all duration-75 border-2 ${
              testState === 'WAITING'
                ? 'bg-[#060913] border-[#1E293B] hover:border-slate-700'
                : testState === 'STIMULUS'
                ? 'bg-[#38BDF8] border-white shadow-[0_0_30px_rgba(56,189,248,0.8)]'
                : feedbackMsg.includes('LAPSE') || feedbackMsg.includes('FALSE')
                ? 'bg-rose-950/40 border-rose-500/60'
                : 'bg-emerald-950/40 border-emerald-500/60'
            }`}
          >
            {testState === 'WAITING' && (
              <span className="font-mono text-xs tracking-widest text-slate-500 animate-pulse">
                READY... WAIT FOR FLASH
              </span>
            )}
            {testState === 'STIMULUS' && (
              <span className="font-mono text-2xl font-black tracking-widest text-[#060913]">
                TAP NOW!
              </span>
            )}
            {testState === 'FEEDBACK' && (
              <div className="text-center">
                <span className={`font-mono text-xl font-bold ${
                  feedbackMsg.includes('LAPSE') || feedbackMsg.includes('FALSE')
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}>
                  {feedbackMsg}
                </span>
                <p className="text-[10px] font-mono text-slate-400 mt-1">Preparing next stimulus...</p>
              </div>
            )}
          </div>
        </div>
      )}

      {testState === 'SUBMITTING' && (
        <div className="py-12 flex flex-col items-center justify-center space-y-3">
          <RefreshCw className="h-6 w-6 text-[#38BDF8] animate-spin" />
          <p className="text-xs font-mono text-slate-400">Calculating Psychomotor Performance Vectors...</p>
        </div>
      )}

      {testState === 'DONE' && lastSession && (
        <div className="space-y-4 py-2">
          <div className="p-4 rounded-lg bg-[#060913] border border-[#1E293B] grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
            <div>
              <p className="text-[10px] font-mono text-slate-400 uppercase">Mean Reaction Time</p>
              <p className="text-lg font-bold font-mono text-white mt-0.5">
                {lastSession.avg_reaction_time_ms} <span className="text-xs text-slate-400 font-normal">ms</span>
              </p>
            </div>
            <div>
              <p className="text-[10px] font-mono text-slate-400 uppercase">Median RT</p>
              <p className="text-lg font-bold font-mono text-sky-400 mt-0.5">
                {lastSession.median_reaction_time_ms} <span className="text-xs text-slate-400 font-normal">ms</span>
              </p>
            </div>
            <div>
              <p className="text-[10px] font-mono text-slate-400 uppercase">Lapses (&gt;500ms)</p>
              <p className={`text-lg font-bold font-mono mt-0.5 ${lastSession.lapses_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {lastSession.lapses_count}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-mono text-slate-400 uppercase">Rating</p>
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold font-mono mt-1 ${
                lastSession.performance_rating === 'OPTIMAL'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : lastSession.performance_rating === 'NORMAL'
                  ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}>
                {lastSession.performance_rating}
              </span>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleStartTest}
              className="px-4 py-2 rounded-lg bg-[#1E293B] text-slate-200 hover:text-white font-mono text-xs font-semibold flex items-center space-x-1.5 transition-colors border border-slate-700"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Retest Battery</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
