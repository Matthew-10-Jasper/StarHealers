import React, { useState } from 'react';
import MetricCard from '../../common/MetricCard';
import MetricDetailModal from './MetricDetailModal';
import VitalsChart from './VitalsChart';
import { METRIC_DEFINITIONS } from '../../../data/mockData';
import { Activity, Play, Pause, RefreshCw, Zap, ShieldAlert, Filter } from 'lucide-react';

export default function VitalsDashboard({
  astronaut,
  readings,
  historicalData,
  timeRange,
  onChangeTimeRange,
  isLiveSimulating,
  onToggleLiveSimulating,
  onInjectScenario,
}) {
  const [selectedMetricKey, setSelectedMetricKey] = useState('heartRate');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState('all'); // 'all' | 'cardio' | 'respiratory' | 'metabolic' | 'neuro'

  const handleCardClick = (key) => {
    setSelectedMetricKey(key);
    setIsModalOpen(true);
  };

  const metricCategories = {
    all: Object.keys(METRIC_DEFINITIONS),
    cardio: ['heartRate', 'hrv', 'bloodPressure'],
    respiratory: ['spo2'],
    metabolic: ['glucose', 'hydration', 'temperature'],
    neuro: ['sleep', 'stress'],
  };

  const filteredKeys = metricCategories[filterCategory] || Object.keys(METRIC_DEFINITIONS);

  return (
    <div className="space-y-6">
      {/* Module 1 Header & Live Simulation Controls */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <h2 className="text-lg font-bold text-slate-100 font-sans tracking-wide">
              Module 1: Astronaut Health Monitoring
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/40">
              Core Vitals & Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Real-time multi-channel physiological monitoring for deep-space mission crew.
          </p>
        </div>

        {/* Live Simulator & Scenario Injection Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Stream Control */}
          <button
            onClick={onToggleLiveSimulating}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition ${
              isLiveSimulating
                ? 'bg-cyan-950/60 border-cyan-500/50 text-cyan-300'
                : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
          >
            {isLiveSimulating ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-cyan-400" />}
            <span>{isLiveSimulating ? 'Pause Stream' : 'Resume Stream'}</span>
          </button>

          {/* Demonstration Scenario Injectors */}
          <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className="text-slate-400 px-2 text-[10px]">SCENARIO:</span>
            <button
              onClick={() => onInjectScenario('nominal')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-slate-300 text-[11px] transition"
              title="Reset astronaut vitals to nominal baseline"
            >
              Nominal
            </button>
            <button
              onClick={() => onInjectScenario('fatigue')}
              className="px-2 py-1 rounded hover:bg-amber-950/40 text-amber-300 text-[11px] transition"
              title="Inject Autonomic Fatigue (Elevated HR, Reduced HRV, Stress spike)"
            >
              Fatigue
            </button>
            <button
              onClick={() => onInjectScenario('hypoxia')}
              className="px-2 py-1 rounded hover:bg-rose-950/40 text-rose-300 text-[11px] transition"
              title="Inject Acute Hypoxia (SpO2 drop to 90%, Tachycardia)"
            >
              Hypoxia
            </button>
            <button
              onClick={() => onInjectScenario('nodata')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-slate-400 text-[11px] transition"
              title="Simulate sensor packet loss / No data"
            >
              No Data
            </button>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-mono">
        <span className="text-slate-400 flex items-center gap-1 text-[11px]">
          <Filter className="w-3 h-3 text-cyan-400" /> SYSTEM FILTER:
        </span>
        {[
          { id: 'all', label: 'All Vitals (9)' },
          { id: 'cardio', label: 'Cardiovascular (3)' },
          { id: 'respiratory', label: 'Respiratory (1)' },
          { id: 'metabolic', label: 'Metabolic & Renal (3)' },
          { id: 'neuro', label: 'Neuro-Cognitive (2)' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterCategory(tab.id)}
            className={`px-3 py-1.5 rounded-lg border transition whitespace-nowrap ${
              filterCategory === tab.id
                ? 'bg-cyan-950/80 border-cyan-500/50 text-cyan-300 font-semibold'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Grid of Metric Cards (Palette 2: Cyan & Blue) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredKeys.map((key) => (
          <MetricCard
            key={key}
            metricKey={key}
            metricDef={METRIC_DEFINITIONS[key]}
            reading={readings?.[key]}
            isSelected={selectedMetricKey === key}
            onClick={() => handleCardClick(key)}
          />
        ))}
      </div>

      {/* Historical Telemetry Chart (Recharts) */}
      <VitalsChart
        historicalData={historicalData}
        selectedMetric={selectedMetricKey}
        onSelectMetric={setSelectedMetricKey}
        timeRange={timeRange}
        onChangeTimeRange={onChangeTimeRange}
        astronaut={astronaut}
      />

      {/* Click-through Detail Modal */}
      <MetricDetailModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        metricKey={selectedMetricKey}
        metricDef={METRIC_DEFINITIONS[selectedMetricKey]}
        reading={readings?.[selectedMetricKey]}
        astronaut={astronaut}
        historicalData={historicalData}
      />
    </div>
  );
}
