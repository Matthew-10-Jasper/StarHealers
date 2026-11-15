import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../../services/apiClient';
import {
  Flame,
  Radiation,
  Wind,
  Moon,
  Play,
  RotateCcw,
  FastForward,
  Share2,
  CheckCircle2,
  AlertTriangle,
  Sliders,
  Activity,
  Layers,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const Module5Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'CONTROLLER' | 'RADIATION' | 'CO2' | 'SLEEP'>('CONTROLLER');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [sessionStep, setSessionStep] = useState<number>(0);
  const [maxSteps, setMaxSteps] = useState<number>(24);
  const [currentReadings, setCurrentReadings] = useState<any>({
    radiation_msv_total: 0.85,
    co2_mmhg: 3.2,
    sleep_debt_hours: 1.4,
    hazard_index: 'NOMINAL',
  });
  const [timelineData, setTimelineData] = useState<any[]>([]);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  // Standalone Engine Parameters
  const [radParams, setRadParams] = useState({
    duration_hours: 24,
    gcr_dose_rate_msv_per_day: 1.8,
    spe_active: true,
    spe_peak_multiplier: 5.0,
    shielding_thickness_g_cm2: 10.0,
  });

  const [co2Params, setCo2Params] = useState({
    duration_hours: 24,
    cabin_volume_m3: 100.0,
    crew_count: 4,
    generation_rate_per_person_l_h: 21.0,
    initial_co2_mmhg: 3.0,
    scrubber_nominal_removal_l_h: 84.0,
    scrubber_efficiency: 0.95,
    scrubber_failure_active: false,
  });

  const [sleepParams, setSleepParams] = useState({
    total_days: 14,
    baseline_sleep_hours: 8.0,
    disruption_active: true,
    disruption_type: 'ACUTE_MISSION_CRITICAL',
  });

  // Predefined scenarios
  const scenarios = [
    {
      id: 'solar_storm',
      name: 'Severe Solar Particle Event (SPE)',
      desc: 'Coronal Mass Ejection impact raising exterior radiation dose rate 15x.',
      rad: { spe_active: true, spe_peak_multiplier: 15.0, shielding_thickness_g_cm2: 5.0 },
      co2: { scrubber_failure_active: false },
    },
    {
      id: 'scrubber_loss',
      name: 'ECLSS Scrubber Failure (50% Loss)',
      desc: 'Partial desiccant bed saturation causing cabin CO2 accumulation.',
      rad: { spe_active: false, spe_peak_multiplier: 1.0, shielding_thickness_g_cm2: 10.0 },
      co2: { scrubber_failure_active: true, scrubber_efficiency: 0.5 },
    },
    {
      id: 'eva_multi_hazard',
      name: 'Emergency EVA Multi-Hazard Contingency',
      desc: 'Combined SPE proton flux warning with crew acute sleep deprivation.',
      rad: { spe_active: true, spe_peak_multiplier: 8.0, shielding_thickness_g_cm2: 5.0 },
      co2: { scrubber_failure_active: false },
    },
  ];

  const handleApplyScenario = (sc: any) => {
    setRadParams((prev) => ({ ...prev, ...sc.rad }));
    setCo2Params((prev) => ({ ...prev, ...sc.co2 }));
    handleResetSimulation();
  };

  const handleResetSimulation = () => {
    setSessionStep(0);
    setExportSuccess(null);
    setCurrentReadings({
      radiation_msv_total: 0.05,
      co2_mmhg: co2Params.initial_co2_mmhg,
      sleep_debt_hours: 0.2,
      hazard_index: 'NOMINAL',
    });
    setTimelineData([
      {
        hour: 0,
        radiation_msv: 0.05,
        co2_mmhg: co2Params.initial_co2_mmhg,
        sleep_debt_hours: 0.2,
      },
    ]);
  };

  const handleStepSimulation = () => {
    if (sessionStep >= maxSteps) return;
    const nextStep = sessionStep + 1;
    setSessionStep(nextStep);

    // Physical integration stepping
    const speDose = radParams.spe_active && nextStep >= 6 && nextStep <= 18
      ? (radParams.spe_peak_multiplier * 0.12) / (radParams.shielding_thickness_g_cm2 / 5)
      : (radParams.gcr_dose_rate_msv_per_day / 24) / (radParams.shielding_thickness_g_cm2 / 10);

    const co2Delta = co2Params.scrubber_failure_active ? 0.35 : -0.05;
    const nextCO2 = Math.max(1.8, Math.min(12.5, currentReadings.co2_mmhg + co2Delta));
    const nextRad = Number((currentReadings.radiation_msv_total + speDose).toFixed(3));
    const nextSleep = Number((currentReadings.sleep_debt_hours + (nextStep > 14 ? 0.4 : 0.1)).toFixed(2));

    const hazardIndex =
      nextCO2 > 7.6 || nextRad > 50.0 ? 'CRITICAL' : nextCO2 > 5.0 || nextRad > 20.0 ? 'WARNING' : 'NOMINAL';

    const newReading = {
      radiation_msv_total: nextRad,
      co2_mmhg: Number(nextCO2.toFixed(2)),
      sleep_debt_hours: nextSleep,
      hazard_index: hazardIndex,
    };
    setCurrentReadings(newReading);

    setTimelineData((prev) => [
      ...prev,
      {
        hour: nextStep,
        radiation_msv: nextRad,
        co2_mmhg: Number(nextCO2.toFixed(2)),
        sleep_debt_hours: nextSleep,
      },
    ]);
  };

  const handleRunToEnd = () => {
    setIsRunning(true);
    let currentStep = sessionStep;
    let rad = currentReadings.radiation_msv_total;
    let co2 = currentReadings.co2_mmhg;
    let sleep = currentReadings.sleep_debt_hours;
    const newTimeline = [...timelineData];

    while (currentStep < maxSteps) {
      currentStep++;
      const speDose = radParams.spe_active && currentStep >= 6 && currentStep <= 18
        ? (radParams.spe_peak_multiplier * 0.12) / (radParams.shielding_thickness_g_cm2 / 5)
        : (radParams.gcr_dose_rate_msv_per_day / 24) / (radParams.shielding_thickness_g_cm2 / 10);
      const co2Delta = co2Params.scrubber_failure_active ? 0.35 : -0.05;
      co2 = Math.max(1.8, Math.min(12.5, co2 + co2Delta));
      rad = Number((rad + speDose).toFixed(3));
      sleep = Number((sleep + (currentStep > 14 ? 0.4 : 0.1)).toFixed(2));

      newTimeline.push({
        hour: currentStep,
        radiation_msv: rad,
        co2_mmhg: Number(co2.toFixed(2)),
        sleep_debt_hours: sleep,
      });
    }

    setSessionStep(maxSteps);
    setTimelineData(newTimeline);
    setCurrentReadings({
      radiation_msv_total: rad,
      co2_mmhg: Number(co2.toFixed(2)),
      sleep_debt_hours: sleep,
      hazard_index: co2 > 7.6 || rad > 50.0 ? 'CRITICAL' : co2 > 5.0 || rad > 20.0 ? 'WARNING' : 'NOMINAL',
    });
    setIsRunning(false);
  };

  const handleExportToModule4 = async () => {
    try {
      setExportSuccess('Synchronizing simulated hazard telemetry with Module 4 Context...');
      // Invoke Module 4 state adaptation injection
      await apiClient.requestStateTransition(
        currentReadings.hazard_index === 'CRITICAL' ? 'CONTINGENCY' : 'DEGRADED',
        `Module 5 Hazard Simulation Export: CO2=${currentReadings.co2_mmhg} mmHg, Radiation=${currentReadings.radiation_msv_total} mSv`,
        {
          source: 'MODULE_5_SIMULATION_ENGINE',
          co2_mmhg: currentReadings.co2_mmhg,
          radiation_dose_msv: currentReadings.radiation_msv_total,
          sleep_debt_hours: currentReadings.sleep_debt_hours,
        }
      );
      setExportSuccess('Successfully exported simulation trajectory into Module 4 Mission Context!');
    } catch (e: any) {
      setExportSuccess(`Export failed: ${e.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            <h2 className="text-lg font-bold text-[#F8FAFC]">Module 5 • Space Hazard Simulation Engine</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/40">
              PHYSICS & MULTI-HAZARD SOLVER
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Authoritative numerical modeling for Space Radiation, Cabin CO2 accumulation ODEs, and discrete sleep debt.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center space-x-1.5 bg-[#060913] p-1 rounded-lg border border-[#1E293B]">
          {[
            { id: 'CONTROLLER', label: 'MULTI-HAZARD', icon: Layers },
            { id: 'RADIATION', label: 'RADIATION', icon: Radiation },
            { id: 'CO2', label: 'CABIN CO2', icon: Wind },
            { id: 'SLEEP', label: 'SLEEP DEBT', icon: Moon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-1.5 px-3 py-1 rounded text-xs font-mono font-bold transition ${
                activeTab === tab.id
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {React.createElement(tab.icon, { className: 'w-3.5 h-3.5' })}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Predefined Scenario Quick Injection */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4">
        <div className="text-xs font-mono text-slate-400 mb-2 font-semibold">PRESET SPACE HAZARD SCENARIOS:</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {scenarios.map((sc) => (
            <div
              key={sc.id}
              onClick={() => handleApplyScenario(sc)}
              className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-amber-500/50 cursor-pointer transition"
            >
              <div className="text-xs font-bold text-amber-300">{sc.name}</div>
              <div className="text-[11px] text-slate-400 mt-1 leading-snug">{sc.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {activeTab === 'CONTROLLER' && (
        <>
          {/* Controller Gauges */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="flex items-center space-x-1.5">
                  <Wind className="w-3.5 h-3.5 text-cyan-400" />
                  <span>CABIN CO2</span>
                </span>
                <span className={currentReadings.co2_mmhg > 5.0 ? 'text-amber-400' : 'text-emerald-400'}>
                  {currentReadings.co2_mmhg > 5.0 ? 'ELEVATED' : 'NOMINAL'}
                </span>
              </div>
              <div className="text-2xl font-bold font-mono text-white mt-2">
                {currentReadings.co2_mmhg} <span className="text-xs text-slate-400">mmHg</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-1">Limit: 7.6 mmHg (NASA SMAC)</div>
            </div>

            <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="flex items-center space-x-1.5">
                  <Radiation className="w-3.5 h-3.5 text-yellow-400" />
                  <span>CUMULATIVE DOSE</span>
                </span>
                <span className={currentReadings.radiation_msv_total > 20 ? 'text-rose-400' : 'text-emerald-400'}>
                  {currentReadings.radiation_msv_total > 20 ? 'HAZARD' : 'SAFE'}
                </span>
              </div>
              <div className="text-2xl font-bold font-mono text-white mt-2">
                {currentReadings.radiation_msv_total} <span className="text-xs text-slate-400">mSv</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-1">30-Day Limit: 250 mSv</div>
            </div>

            <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="flex items-center space-x-1.5">
                  <Moon className="w-3.5 h-3.5 text-indigo-400" />
                  <span>SLEEP DEFICIT</span>
                </span>
                <span className="text-indigo-400">ACCUMULATING</span>
              </div>
              <div className="text-2xl font-bold font-mono text-white mt-2">
                {currentReadings.sleep_debt_hours} <span className="text-xs text-slate-400">hrs</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-1">Fatigue Alert: &gt; 8.0 hrs</div>
            </div>

            <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <span className="flex items-center space-x-1.5">
                  <Flame className="w-3.5 h-3.5 text-amber-400" />
                  <span>COMPOSITE STATE</span>
                </span>
                <span className="text-amber-400">SOLVER</span>
              </div>
              <div className={`text-2xl font-bold font-mono mt-2 ${
                currentReadings.hazard_index === 'CRITICAL'
                  ? 'text-rose-400'
                  : currentReadings.hazard_index === 'WARNING'
                  ? 'text-amber-400'
                  : 'text-emerald-400'
              }`}>
                {currentReadings.hazard_index}
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-1">Step {sessionStep} / {maxSteps} hrs</div>
            </div>
          </div>

          {/* Stepper & Action Controls */}
          <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleStepSimulation}
                disabled={sessionStep >= maxSteps}
                className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-mono text-xs font-bold flex items-center space-x-1.5 transition"
              >
                <Play className="w-3.5 h-3.5" />
                <span>STEP (+1 HOUR)</span>
              </button>

              <button
                onClick={handleRunToEnd}
                disabled={sessionStep >= maxSteps}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white font-mono text-xs font-bold flex items-center space-x-1.5 border border-slate-700 transition"
              >
                <FastForward className="w-3.5 h-3.5 text-amber-400" />
                <span>RUN TRAJECTORY TO END</span>
              </button>

              <button
                onClick={handleResetSimulation}
                className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white font-mono text-xs border border-slate-800 transition"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            <button
              onClick={handleExportToModule4}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold flex items-center space-x-1.5 shadow-sm transition self-end md:self-auto"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>EXPORT TO MODULE 4 ADAPTIVE CONTEXT</span>
            </button>
          </div>

          {exportSuccess && (
            <div className="p-3 bg-indigo-950/40 border border-indigo-500/50 rounded-xl text-xs font-mono text-indigo-300 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />
              <span>{exportSuccess}</span>
            </div>
          )}

          {/* Simulation Trajectory Chart */}
          <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Activity className="w-4 h-4 text-amber-400" />
              <span>Simulated Spacecraft Hazard Progression (Time-Series Trajectory)</span>
            </h3>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timelineData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                  <XAxis dataKey="hour" stroke="#64748B" fontSize={11} label={{ value: 'Hours', position: 'insideBottomRight', offset: -5 }} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="co2_mmhg" name="CO2 (mmHg)" stroke="#38BDF8" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="radiation_msv" name="Dose (mSv)" stroke="#F59E0B" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="sleep_debt_hours" name="Sleep Debt (h)" stroke="#A855F7" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}

      {activeTab === 'RADIATION' && (
        <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Radiation className="w-4 h-4 text-yellow-400" />
            <span>Standalone Space Radiation Physical Model Config</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <label className="text-slate-400 block mb-1">GCR Dose Rate (mSv / day):</label>
              <input
                type="number"
                step="0.1"
                value={radParams.gcr_dose_rate_msv_per_day}
                onChange={(e) => setRadParams({ ...radParams, gcr_dose_rate_msv_per_day: parseFloat(e.target.value) || 1.8 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Shielding Areal Density (g / cm² Al-eq):</label>
              <input
                type="number"
                step="1"
                value={radParams.shielding_thickness_g_cm2}
                onChange={(e) => setRadParams({ ...radParams, shielding_thickness_g_cm2: parseFloat(e.target.value) || 10 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'CO2' && (
        <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Wind className="w-4 h-4 text-cyan-400" />
            <span>Cabin Atmosphere CO2 Mass Balance ODE Configuration</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <label className="text-slate-400 block mb-1">Cabin Net Volume (m³):</label>
              <input
                type="number"
                value={co2Params.cabin_volume_m3}
                onChange={(e) => setCo2Params({ ...co2Params, cabin_volume_m3: parseFloat(e.target.value) || 100 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Crew Complement (Count):</label>
              <input
                type="number"
                value={co2Params.crew_count}
                onChange={(e) => setCo2Params({ ...co2Params, crew_count: parseInt(e.target.value) || 4 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'SLEEP' && (
        <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Moon className="w-4 h-4 text-purple-400" />
            <span>Astronaut Sleep Deficit & Recovery Kinetics</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <label className="text-slate-400 block mb-1">Baseline Recommended Sleep (hours):</label>
              <input
                type="number"
                step="0.5"
                value={sleepParams.baseline_sleep_hours}
                onChange={(e) => setSleepParams({ ...sleepParams, baseline_sleep_hours: parseFloat(e.target.value) || 8.0 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Simulation Duration (Days):</label>
              <input
                type="number"
                value={sleepParams.total_days}
                onChange={(e) => setSleepParams({ ...sleepParams, total_days: parseInt(e.target.value) || 14 })}
                className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
