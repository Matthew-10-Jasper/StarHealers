import React, { useState } from 'react';
import Modal from '../../common/Modal';
import { Sliders, Check, RotateCcw } from 'lucide-react';

export default function RuleConfigModal({ isOpen, onClose }) {
  const [rules, setRules] = useState({
    hrMax: 105,
    hrMin: 50,
    hrvMin: 40,
    spo2Critical: 92,
    spo2Warning: 94,
    sleepMinHours: 5.5,
    stressThreshold: 65,
    compoundRuleEnabled: true,
  });

  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => {
      setSavedSuccess(false);
      onClose();
    }, 800);
  };

  const handleReset = () => {
    setRules({
      hrMax: 105,
      hrMin: 50,
      hrvMin: 40,
      spo2Critical: 92,
      spo2Warning: 94,
      sleepMinHours: 5.5,
      stressThreshold: 65,
      compoundRuleEnabled: true,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Rule Engine Threshold Configuration"
      subtitle="Module 3: Configurable Aerospace Medical Triage Rules"
      maxWidth="max-w-2xl"
    >
      <div className="space-y-5">
        <p className="text-xs text-slate-300 leading-relaxed">
          Configure baseline decision-support thresholds utilized by the autonomous rule engine. Alert triggers and severity classifications recalculate immediately upon parameter adjustments.
        </p>

        {/* Rule parameter sliders & inputs */}
        <div className="space-y-4">
          {/* Heart Rate Max (Tachycardia) */}
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-200 block">
                Resting Tachycardia Upper Bound
              </label>
              <span className="text-[10px] font-mono text-slate-400">
                Rule ID: RULE-CARDIO-HR-01 | Unit: bpm
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={rules.hrMax}
                onChange={(e) => setRules({ ...rules, hrMax: Number(e.target.value) })}
                className="w-18 px-2.5 py-1 rounded bg-slate-950 border border-slate-700 text-xs font-mono text-cyan-400 text-right focus:outline-none focus:border-cyan-400"
              />
              <span className="text-xs font-mono text-slate-400 w-8">bpm</span>
            </div>
          </div>

          {/* HRV Minimum Threshold */}
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-200 block">
                Vagal Tone HRV Suppression Floor
              </label>
              <span className="text-[10px] font-mono text-slate-400">
                Rule ID: RULE-AUTONOMIC-HRV-02 | Unit: ms
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={rules.hrvMin}
                onChange={(e) => setRules({ ...rules, hrvMin: Number(e.target.value) })}
                className="w-18 px-2.5 py-1 rounded bg-slate-950 border border-slate-700 text-xs font-mono text-cyan-400 text-right focus:outline-none focus:border-cyan-400"
              />
              <span className="text-xs font-mono text-slate-400 w-8">ms</span>
            </div>
          </div>

          {/* SpO2 Critical Threshold */}
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-200 block">
                Acute SpO2 Hypoxemia Trigger
              </label>
              <span className="text-[10px] font-mono text-slate-400">
                Rule ID: RULE-HYPOXIA-ACUTE-01 | Unit: %
              </span>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={rules.spo2Critical}
                onChange={(e) => setRules({ ...rules, spo2Critical: Number(e.target.value) })}
                className="w-18 px-2.5 py-1 rounded bg-slate-950 border border-slate-700 text-xs font-mono text-rose-400 text-right focus:outline-none focus:border-rose-400"
              />
              <span className="text-xs font-mono text-slate-400 w-8">%</span>
            </div>
          </div>

          {/* Compound Rule Toggle */}
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <label className="text-xs font-semibold text-slate-200 block">
                Enable Multi-Signal Compound Fatigue Logic
              </label>
              <span className="text-[10px] font-mono text-slate-400">
                Correlates (HR elevated + HRV low + Sleep &lt; 5.5h + Stress &gt; 65)
              </span>
            </div>
            <input
              type="checkbox"
              checked={rules.compoundRuleEnabled}
              onChange={(e) => setRules({ ...rules, compoundRuleEnabled: e.target.checked })}
              className="w-4 h-4 rounded text-cyan-500 focus:ring-cyan-400 cursor-pointer"
            />
          </div>
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset to NASA Standards</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-semibold transition shadow-cyan-glow"
            >
              {savedSuccess ? <Check className="w-4 h-4 text-emerald-300" /> : <Sliders className="w-3.5 h-3.5" />}
              <span>{savedSuccess ? 'Config Saved!' : 'Apply Thresholds'}</span>
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
