import React, { useState, useEffect } from 'react';
import { useSharedMission } from '../../context/SharedMissionContext';
import { apiClient } from '../../services/apiClient';
import {
  Activity,
  RotateCw,
  ShieldAlert,
  ShieldCheck,
  Heart,
  Brain,
  Wind,
  Eye,
  AlertTriangle,
} from 'lucide-react';

export const Module2Dashboard: React.FC = () => {
  const { selectedAstronaut } = useSharedMission();
  const [selectedRegion, setSelectedRegion] = useState<string>('heart');
  const [viewMode, setViewMode] = useState<'front' | 'back'>('front');
  const [regionData, setRegionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const regionDefinitions: Record<string, { label: string; icon: any; summary: string }> = {
    brain: {
      label: 'Neuro & Cognitive State',
      icon: Brain,
      summary: 'Monitors intracranial pressure, cognitive fatigue index, and psychomotor latency.',
    },
    heart: {
      label: 'Cardiovascular System',
      icon: Heart,
      summary: 'Monitors myocardial strain, arterial blood pressure, and autonomic HRV balance.',
    },
    lungs: {
      label: 'Pulmonary / Respiratory',
      icon: Wind,
      summary: 'Monitors oxygen diffusion, peripheral SpO2, and respiratory rate under cabin pressure.',
    },
    spine: {
      label: 'Spinal / Musculoskeletal',
      icon: Activity,
      summary: 'Monitors microgravity spinal elongation, bone mineral density, and lumbar stress.',
    },
    eyes: {
      label: 'Visual & SANS Risk',
      icon: Eye,
      summary: 'Spaceflight-Associated Neuro-ocular Syndrome (SANS) optic disc edema evaluation.',
    },
    metabolic: {
      label: 'Metabolic & Fluid Balance',
      icon: Activity,
      summary: 'Monitors plasma volume shift, bioimpedance hydration, and core thermal regulation.',
    },
  };

  useEffect(() => {
    let active = true;
    async function loadRegion() {
      try {
        setIsLoading(true);
        const data = await apiClient.getBodyRegionDetail(selectedAstronaut.id, selectedRegion);
        if (active) setRegionData(data);
      } catch (e) {
        // Fallback simulated detailed region telemetry
        if (active) {
          setRegionData({
            region: selectedRegion,
            status: selectedAstronaut.id === 'ASTRO-01' && selectedRegion === 'heart' ? 'WARNING' : 'NORMAL',
            metrics: {
              perfusion_index: '94%',
              tissue_oxygenation: '96.5%',
              strain_score: selectedRegion === 'heart' ? '42/100' : '18/100',
              vulnerability_flag: selectedRegion === 'heart' ? 'ELEVATED_HEART_RATE_UNDER_G' : 'NONE',
            },
            clinical_observations: [
              'No focal ischemia detected on multi-channel sensors.',
              'Microgravity cephalad fluid redistribution within expected bounds.',
            ],
          });
        }
      } finally {
        if (active) setIsLoading(false);
      }
    }
    loadRegion();
    return () => {
      active = false;
    };
  }, [selectedAstronaut.id, selectedRegion]);

  const getRegionStatus = (region: string) => {
    if (selectedAstronaut.id === 'ASTRO-01') {
      if (region === 'heart' || region === 'brain') return 'WARNING';
    }
    return 'NORMAL';
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CRITICAL':
        return 'bg-rose-950/70 border-rose-500 text-rose-300';
      case 'WARNING':
        return 'bg-amber-950/70 border-amber-500 text-amber-300';
      case 'NORMAL':
      default:
        return 'bg-emerald-950/70 border-emerald-500 text-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-pulse" />
            <h2 className="text-lg font-bold text-[#F8FAFC]">Module 2 • Interactive Anatomical Body Map</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800/40">
              ORGAN TELEMETRY
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Biometric projection for <span className="text-white font-semibold">{selectedAstronaut.name}</span> ({selectedAstronaut.id}).
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode(viewMode === 'front' ? 'back' : 'front')}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-700 text-slate-300 hover:text-white transition"
          >
            <RotateCw className="w-3.5 h-3.5 text-purple-400" />
            <span>ROTATE TO {viewMode === 'front' ? 'BACK' : 'FRONT'} VIEW</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Body Model & Detail Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Anatomical Model (Left) */}
        <div className="lg:col-span-6 bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-6 flex flex-col items-center justify-center relative min-h-[460px]">
          <div className="absolute top-4 left-4 text-xs font-mono text-slate-400">
            VIEW: <span className="text-purple-400 font-bold uppercase">{viewMode} PROJECTION</span>
          </div>

          {/* Interactive SVG Body Silhouette */}
          <div className="w-full max-w-[280px] h-[380px] relative flex items-center justify-center">
            <svg
              viewBox="0 0 200 400"
              className="w-full h-full drop-shadow-[0_0_20px_rgba(168,85,247,0.15)]"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Silhouette Outline */}
              <path
                d="M100 20 C112 20 120 28 120 40 C120 52 112 60 100 60 C88 60 80 52 80 40 C80 28 88 20 100 20 Z
                   M85 62 L60 75 L45 150 L55 152 L68 95 L72 170 L65 280 L55 370 L75 375 L88 280 L96 180 L104 180 L112 280 L125 375 L145 370 L135 280 L128 170 L132 95 L145 152 L155 150 L140 75 L115 62 Z"
                fill="#1E293B"
                stroke="#334155"
                strokeWidth="2"
              />

              {/* Head / Brain Region */}
              <circle
                cx="100"
                cy="38"
                r="16"
                className="cursor-pointer transition-all duration-300 hover:opacity-90"
                fill={selectedRegion === 'brain' ? '#A855F7' : getRegionStatus('brain') === 'WARNING' ? '#F59E0B' : '#10B981'}
                opacity={selectedRegion === 'brain' ? 0.85 : 0.45}
                onClick={() => setSelectedRegion('brain')}
              />
              <text x="100" y="42" textAnchor="middle" fontSize="9" fill="#FFFFFF" fontWeight="bold" pointerEvents="none">
                BRAIN
              </text>

              {/* Eyes Region (Front only) */}
              {viewMode === 'front' && (
                <circle
                  cx="100"
                  cy="32"
                  r="5"
                  className="cursor-pointer"
                  fill={selectedRegion === 'eyes' ? '#A855F7' : '#0EA5E9'}
                  opacity={selectedRegion === 'eyes' ? 0.9 : 0.6}
                  onClick={() => setSelectedRegion('eyes')}
                />
              )}

              {/* Heart Region (Left Chest) */}
              <circle
                cx={viewMode === 'front' ? '108' : '92'}
                cy="100"
                r="14"
                className="cursor-pointer transition-all duration-300 hover:opacity-90 animate-pulse"
                fill={selectedRegion === 'heart' ? '#A855F7' : getRegionStatus('heart') === 'WARNING' ? '#F43F5E' : '#10B981'}
                opacity={selectedRegion === 'heart' ? 0.9 : 0.6}
                onClick={() => setSelectedRegion('heart')}
              />
              <text
                x={viewMode === 'front' ? '108' : '92'}
                y="104"
                textAnchor="middle"
                fontSize="8"
                fill="#FFFFFF"
                fontWeight="bold"
                pointerEvents="none"
              >
                HEART
              </text>

              {/* Lungs Region */}
              <ellipse
                cx="86"
                cy="102"
                rx="9"
                ry="15"
                className="cursor-pointer"
                fill={selectedRegion === 'lungs' ? '#A855F7' : '#10B981'}
                opacity={selectedRegion === 'lungs' ? 0.8 : 0.35}
                onClick={() => setSelectedRegion('lungs')}
              />
              <ellipse
                cx="114"
                cy="102"
                rx="9"
                ry="15"
                className="cursor-pointer"
                fill={selectedRegion === 'lungs' ? '#A855F7' : '#10B981'}
                opacity={selectedRegion === 'lungs' ? 0.8 : 0.35}
                onClick={() => setSelectedRegion('lungs')}
              />

              {/* Spine (Back view prominent) */}
              <line
                x1="100"
                y1="65"
                x2="100"
                y2="170"
                stroke={selectedRegion === 'spine' ? '#A855F7' : '#38BDF8'}
                strokeWidth={viewMode === 'back' ? '6' : '3'}
                strokeDasharray={viewMode === 'back' ? '4 2' : 'none'}
                className="cursor-pointer"
                onClick={() => setSelectedRegion('spine')}
              />

              {/* Musculoskeletal / Limbs Click Points */}
              <circle
                cx="60"
                cy="120"
                r="8"
                className="cursor-pointer"
                fill={selectedRegion === 'metabolic' ? '#A855F7' : '#334155'}
                onClick={() => setSelectedRegion('metabolic')}
              />
              <circle
                cx="140"
                cy="120"
                r="8"
                className="cursor-pointer"
                fill={selectedRegion === 'metabolic' ? '#A855F7' : '#334155'}
                onClick={() => setSelectedRegion('metabolic')}
              />
            </svg>
          </div>

          {/* Organ Quick Selector Buttons */}
          <div className="flex flex-wrap justify-center gap-1.5 mt-4">
            {Object.keys(regionDefinitions).map((key) => (
              <button
                key={key}
                onClick={() => setSelectedRegion(key)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition ${
                  selectedRegion === key
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {regionDefinitions[key].label.split(' ')[0].toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Region Telemetry & Clinical Observations (Right) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md">
            <div className="flex items-center justify-between pb-3 border-b border-[#1E293B] mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-purple-950/40 border border-purple-800/40 text-purple-400">
                  {React.createElement(regionDefinitions[selectedRegion]?.icon || Activity, { className: 'w-5 h-5' })}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    {regionDefinitions[selectedRegion]?.label}
                  </h3>
                  <p className="text-xs text-slate-400">
                    Subject: {selectedAstronaut.name} ({selectedAstronaut.id})
                  </p>
                </div>
              </div>

              <span className={`px-2.5 py-1 rounded border text-xs font-mono font-bold ${getStatusBadge(getRegionStatus(selectedRegion))}`}>
                {getRegionStatus(selectedRegion)}
              </span>
            </div>

            <p className="text-xs text-slate-300 mb-4 leading-relaxed">
              {regionDefinitions[selectedRegion]?.summary}
            </p>

            {/* Telemetry Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-[10px] font-mono text-slate-400">TISSUE PERFUSION</div>
                <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                  {regionData?.metrics?.perfusion_index || '98.2%'}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-[10px] font-mono text-slate-400">LOCAL STRAIN INDEX</div>
                <div className="text-lg font-bold font-mono text-amber-400 mt-0.5">
                  {regionData?.metrics?.strain_score || '24 / 100'}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-[10px] font-mono text-slate-400">MICROGRAVITY COMPLIANCE</div>
                <div className="text-lg font-bold font-mono text-cyan-400 mt-0.5">NOMINAL</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                <div className="text-[10px] font-mono text-slate-400">VULNERABILITY LEVEL</div>
                <div className="text-sm font-bold font-mono text-slate-300 mt-1 truncate">
                  {regionData?.metrics?.vulnerability_flag || 'NONE_DETECTED'}
                </div>
              </div>
            </div>

            {/* Clinical Notes */}
            <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1.5">
              <div className="text-[11px] font-bold text-slate-400 flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                <span>CLINICAL DIAGNOSTIC NOTES:</span>
              </div>
              <p className="text-slate-300 text-[11px]">
                • No acute microgravity muscular atrophy recorded over the last 48h observation window.
              </p>
              <p className="text-slate-300 text-[11px]">
                • Optical telemetry correlates with normal intraocular pressure baseline.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
