import React, { useState, useEffect, useCallback } from 'react';
import { useSharedMission } from '../../context/SharedMissionContext';
import { apiClient } from '../../services/apiClient';
import { METRIC_DEFINITIONS } from '../../data/mockData';
import {
  Heart,
  Activity,
  Wind,
  Thermometer,
  Zap,
  Moon,
  Droplet,
  Play,
  Pause,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  SlidersHorizontal,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const Module1Dashboard: React.FC = () => {
  const { selectedAstronaut } = useSharedMission();
  const [readings, setReadings] = useState<Record<string, any>>({});
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [selectedMetricKey, setSelectedMetricKey] = useState<string>('heartRate');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('24h');
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [chartType, setChartType] = useState<'area' | 'line'>('area');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedDetailMetric, setSelectedDetailMetric] = useState<string | null>(null);

  const fetchVitals = useCallback(async () => {
    try {
      setIsLoading(true);
      const [latest, hist] = await Promise.allSettled([
        apiClient.getLatestHealth(selectedAstronaut.id),
        apiClient.getHealthHistory(selectedAstronaut.id, timeRange),
      ]);

      if (latest.status === 'fulfilled') {
        setReadings(latest.value || {});
      }
      if (hist.status === 'fulfilled' && Array.isArray(hist.value)) {
        setHistoricalData(hist.value);
      } else {
        // Generate fallback historical progression
        const pts = [];
        for (let i = 24; i >= 0; i--) {
          const hr = 72 + Math.sin(i / 3) * 8 + (Math.random() * 4 - 2);
          const hrv = 55 + Math.cos(i / 4) * 12 + (Math.random() * 5);
          const spo2 = 98.2 - (i % 6 === 0 ? 1.5 : 0.2);
          const stress = 28 + Math.sin(i / 2) * 15;
          pts.push({
            time: `${i}h ago`,
            heartRate: Math.round(hr),
            hrv: Math.round(hrv),
            spo2: Number(spo2.toFixed(1)),
            stress: Math.round(stress),
            temperature: 36.8,
            glucose: 95,
          });
        }
        setHistoricalData(pts);
      }
    } catch (err) {
      console.warn('[Module1] Error loading vitals:', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedAstronaut.id, timeRange]);

  useEffect(() => {
    fetchVitals();
    let timer: any = null;
    if (isStreaming) {
      timer = setInterval(fetchVitals, 6000);
    }
    return () => clearInterval(timer);
  }, [fetchVitals, isStreaming]);

  const handleInjectScenario = async (type: string) => {
    try {
      setIsLoading(true);
      const mockReadings: Record<string, any> = {
        nominal: { heartRate: 72, hrv: 58, spo2: 98.5, temperature: 36.8, stress: 24 },
        tachycardia: { heartRate: 135, hrv: 22, spo2: 96.0, temperature: 37.4, stress: 78 },
        hypoxia: { heartRate: 105, hrv: 35, spo2: 89.0, temperature: 36.9, stress: 65 },
        critical: { heartRate: 145, hrv: 18, spo2: 87.5, temperature: 38.6, stress: 92 },
      };
      const payload = mockReadings[type] || mockReadings.nominal;
      await apiClient.injectHealthReading({
        astronaut_id: selectedAstronaut.id,
        metrics: payload,
        scenario: type,
      });
      await fetchVitals();
    } catch (e: any) {
      alert(`Scenario injection failed: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getMetricIcon = (key: string) => {
    switch (key) {
      case 'heartRate':
        return <Heart className="w-4 h-4 text-rose-400" />;
      case 'hrv':
        return <Activity className="w-4 h-4 text-cyan-400" />;
      case 'bloodPressure':
        return <Activity className="w-4 h-4 text-indigo-400" />;
      case 'spo2':
        return <Wind className="w-4 h-4 text-emerald-400" />;
      case 'temperature':
        return <Thermometer className="w-4 h-4 text-amber-400" />;
      case 'glucose':
        return <Zap className="w-4 h-4 text-yellow-400" />;
      case 'sleep':
        return <Moon className="w-4 h-4 text-purple-400" />;
      case 'hydration':
        return <Droplet className="w-4 h-4 text-blue-400" />;
      case 'stress':
      default:
        return <Activity className="w-4 h-4 text-pink-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-950/60 border-rose-500/50';
      case 'WARNING':
        return 'text-amber-400 bg-amber-950/60 border-amber-500/50';
      case 'NORMAL':
        return 'text-emerald-400 bg-emerald-950/60 border-emerald-500/40';
      default:
        return 'text-slate-400 bg-slate-900 border-slate-700';
    }
  };

  const filteredMetricKeys = Object.keys(METRIC_DEFINITIONS).filter((k) => {
    if (selectedCategory === 'all') return true;
    return METRIC_DEFINITIONS[k].category === selectedCategory;
  });

  const chartMetricDef = METRIC_DEFINITIONS[selectedMetricKey] || METRIC_DEFINITIONS.heartRate;

  return (
    <div className="space-y-6">
      {/* Control Banner */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="text-lg font-bold text-[#F8FAFC]">Module 1 • Continuous Astronaut Health Telemetry</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/40">
              SUBA BIO-ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Monitoring subject: <span className="text-white font-semibold">{selectedAstronaut.name}</span> ({selectedAstronaut.id}) — {selectedAstronaut.role}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition ${
              isStreaming
                ? 'bg-emerald-950/50 border-emerald-500/50 text-emerald-300'
                : 'bg-slate-900 border-slate-700 text-slate-400'
            }`}
          >
            {isStreaming ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
            <span>{isStreaming ? 'STREAM ACTIVE' : 'STREAM PAUSED'}</span>
          </button>

          <button
            onClick={fetchVitals}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-700 text-slate-300 hover:text-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-400' : ''}`} />
            <span>SYNC</span>
          </button>

          <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className="text-slate-400 px-2 text-[10px]">SCENARIO:</span>
            <button
              onClick={() => handleInjectScenario('nominal')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-emerald-400 text-[11px]"
            >
              Nominal
            </button>
            <button
              onClick={() => handleInjectScenario('tachycardia')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-amber-400 text-[11px]"
            >
              Tachycardia
            </button>
            <button
              onClick={() => handleInjectScenario('hypoxia')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-rose-400 text-[11px]"
            >
              Hypoxia
            </button>
            <button
              onClick={() => handleInjectScenario('critical')}
              className="px-2 py-1 rounded hover:bg-slate-800 text-red-500 text-[11px]"
            >
              Critical
            </button>
          </div>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2">
        {['all', 'cardio', 'respiratory', 'metabolic', 'neuro'].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1 rounded-lg text-xs font-mono uppercase font-semibold transition ${
              selectedCategory === cat
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50'
                : 'bg-[#0F172A] text-slate-400 hover:text-slate-200 border border-[#1E293B]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* 9 Biometric Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-4">
        {filteredMetricKeys.map((key) => {
          const def = METRIC_DEFINITIONS[key];
          const reading = readings[key] || {};
          const val = reading.value !== undefined ? reading.value : (
            key === 'heartRate' ? 74 :
            key === 'hrv' ? 56 :
            key === 'bloodPressure' ? '120/78' :
            key === 'spo2' ? 98.4 :
            key === 'temperature' ? 36.7 :
            key === 'glucose' ? 92 :
            key === 'sleep' ? 7.6 :
            key === 'hydration' ? 68 :
            32
          );
          const status = reading.status || 'NORMAL';
          const isSelected = selectedMetricKey === key;

          return (
            <div
              key={key}
              onClick={() => {
                setSelectedMetricKey(key);
                setSelectedDetailMetric(key);
              }}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-slate-800/80 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                  : 'bg-[#0F172A]/70 hover:bg-[#0F172A] border-[#1E293B] hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                    {getMetricIcon(key)}
                  </div>
                  <span className="text-xs font-semibold text-slate-300">{def.name}</span>
                </div>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${getStatusColor(status)}`}>
                  {status}
                </span>
              </div>

              <div className="flex items-baseline justify-between mt-3">
                <div className="text-2xl font-bold font-mono text-white tracking-tight">
                  {val} <span className="text-xs text-slate-400 font-normal">{def.unit}</span>
                </div>
                <div className="text-[11px] font-mono text-slate-500">
                  Ref: {def.nominalMin} - {def.nominalMax}
                </div>
              </div>

              <div className="text-[11px] text-slate-400 mt-2 truncate">
                {def.description}
              </div>
            </div>
          );
        })}
      </div>

      {/* Historical Telemetry Chart */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1E293B]">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Telemetry Trend Analysis: {chartMetricDef.name}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/40">
                  {chartMetricDef.unit}
                </span>
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                {selectedAstronaut.name} • {timeRange} telemetry trajectory
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Time Ranges */}
            <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-mono">
              {['1h', '24h', '7d'].map((tr) => (
                <button
                  key={tr}
                  onClick={() => setTimeRange(tr)}
                  className={`px-2.5 py-1 rounded transition ${
                    timeRange === tr
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {tr.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Area/Line Switch */}
            <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs font-mono">
              <button
                onClick={() => setChartType('area')}
                className={`px-2.5 py-1 rounded transition ${
                  chartType === 'area' ? 'bg-slate-800 text-white' : 'text-slate-400'
                }`}
              >
                AREA
              </button>
              <button
                onClick={() => setChartType('line')}
                className={`px-2.5 py-1 rounded transition ${
                  chartType === 'line' ? 'bg-slate-800 text-white' : 'text-slate-400'
                }`}
              >
                LINE
              </button>
            </div>
          </div>
        </div>

        {/* Chart View */}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'area' ? (
              <AreaChart data={historicalData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="metricGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} domain={['dataMin - 5', 'dataMax + 5']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Area
                  type="monotone"
                  dataKey={selectedMetricKey}
                  stroke="#10B981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#metricGrad)"
                />
              </AreaChart>
            ) : (
              <LineChart data={historicalData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} domain={['dataMin - 5', 'dataMax + 5']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#F8FAFC', fontWeight: 'bold' }}
                />
                <Line
                  type="monotone"
                  dataKey={selectedMetricKey}
                  stroke="#38BDF8"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#0284C7' }}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
