import React from 'react';
import {
  Layers,
  Camera,
  Activity,
  GitBranch,
  ShieldAlert,
  Sparkles,
  Moon,
  Sun,
  CheckCircle2,
  Lock,
} from 'lucide-react';

export default function TeammateIntegrationView() {
  const teamModules = [
    {
      palette: 'Palette 1',
      title: 'Webcam rPPG & Pulse Estimation',
      owner: 'Teammate (Matthew)',
      status: 'Reserved for Teammate',
      primaryColor: '#F43F5E',
      secondaryColor: '#FB7185',
      primaryName: 'Bio-Rose',
      secondaryName: 'Soft Coral',
      icon: Camera,
      tech: 'OpenCV / MediaPipe',
      description: 'Facial tracking and optical plethysmography for contactless pulse estimation.',
      isMine: false,
    },
    {
      palette: 'Palette 2',
      title: 'Core Vitals & Telemetry (Module 1)',
      owner: 'Suba (Assigned)',
      status: 'Implemented in Suba Branch',
      primaryColor: '#00F0FF',
      secondaryColor: '#3B82F6',
      primaryName: 'Medical Cyan',
      secondaryName: 'Deep Electric Blue',
      icon: Activity,
      tech: 'React / FastAPI / Recharts / SQLite',
      description: 'Continuous health monitoring, 9 vital metrics, historical charts, and live stream simulator.',
      isMine: true,
    },
    {
      palette: 'Palette 3',
      title: 'Enhanced Statistical Anomaly Engine',
      owner: 'Teammate (Matthew)',
      status: 'Integration Dock Ready',
      primaryColor: '#8B5CF6',
      secondaryColor: '#D946EF',
      primaryName: 'Telemetry Violet',
      secondaryName: 'Orchid Pink',
      icon: Sparkles,
      tech: 'Python / NumPy (Z-Score)',
      description: 'Z-score rolling statistical anomaly detection. Prepared integration hook for Matthew’s models.',
      isMine: false,
    },
    {
      palette: 'Palette 4',
      title: 'Rule-Based Alert & Triage (Module 3)',
      owner: 'Suba (Assigned)',
      status: 'Implemented in Suba Branch',
      primaryColor: '#EF4444',
      secondaryColor: '#F59E0B',
      primaryName: 'Critical Crimson',
      secondaryName: 'Solar Amber',
      icon: ShieldAlert,
      tech: 'FastAPI / Pydantic / Rules Engine',
      description: 'Transparent explainable clinical rule evaluation, compound multi-signal risk alerts, and escalation steps.',
      isMine: true,
    },
    {
      palette: 'Palette 5',
      title: 'Explainable AI Clinical Advisor',
      owner: 'Teammate',
      status: 'Reserved for Teammate',
      primaryColor: '#10B981',
      secondaryColor: '#14B8A6',
      primaryName: 'Emerald Mint',
      secondaryName: 'Teal Aqua',
      icon: Sparkles,
      tech: 'LLM / Medical RAG Guidelines',
      description: 'Autonomous countermeasure explanations and clinical reasoning tags.',
      isMine: false,
    },
    {
      palette: 'Palette 6',
      title: 'Circadian, Fatigue & Stress (PVT)',
      owner: 'Teammate',
      status: 'Reserved for Teammate',
      primaryColor: '#6366F1',
      secondaryColor: '#38BDF8',
      primaryName: 'Nebula Indigo',
      secondaryName: 'Sky Periwinkle',
      icon: Moon,
      tech: 'Psychomotor Vigilance Task (PVT)',
      description: 'Dedicated sleep architecture and psychomotor cognitive performance testing.',
      isMine: false,
    },
    {
      palette: 'Palette 7',
      title: 'Space Environment & Radiation Hazards',
      owner: 'Shared Feature',
      status: 'Integration Ready',
      primaryColor: '#EAB308',
      secondaryColor: '#F97316',
      primaryName: 'Solar Gold',
      secondaryName: 'Warm Burnt Orange',
      icon: Sun,
      tech: 'ECLSS Habitat Sensor APIs',
      description: 'Galactic cosmic radiation, cabin CO2 scrubbers, microgravity exposure gauges.',
      isMine: false,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Layers className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-white font-sans tracking-wide">
              Shared Team Architecture & Seven-Module Palette System
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
              NASA Hackathon Team Specification
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Strict division of module ownership, clean non-colliding integration contracts, and exact color assignments.
          </p>
        </div>
      </div>

      {/* Grid of 7 Modules with their exact color palettes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {teamModules.map((mod, idx) => {
          const Icon = mod.icon;

          return (
            <div
              key={idx}
              className={`glass-panel rounded-xl p-5 border transition relative ${
                mod.isMine
                  ? 'border-cyan-500/50 bg-slate-900/90 shadow-cyan-glow'
                  : 'border-slate-800/80 bg-slate-950/50'
              }`}
            >
              {/* Top Banner */}
              <div className="flex items-start justify-between gap-2 mb-3">
                <div className="flex items-center gap-2.5">
                  <div
                    className="p-2 rounded-lg"
                    style={{ backgroundColor: `${mod.primaryColor}20`, color: mod.primaryColor }}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono tracking-wider text-slate-400 block uppercase">
                      {mod.palette}
                    </span>
                    <h3 className="text-sm font-bold text-white font-sans">{mod.title}</h3>
                  </div>
                </div>

                {mod.isMine ? (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-semibold shrink-0">
                    MY MODULE
                  </span>
                ) : (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800 shrink-0">
                    {mod.owner.split(' ')[0]}
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-4 min-h-[40px]">
                {mod.description}
              </p>

              {/* Exact Colors Bar */}
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2 mb-4">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Primary: {mod.primaryName}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-200">{mod.primaryColor}</span>
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-slate-700 inline-block"
                      style={{ backgroundColor: mod.primaryColor }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Secondary: {mod.secondaryName}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-200">{mod.secondaryColor}</span>
                    <span
                      className="w-3.5 h-3.5 rounded-full border border-slate-700 inline-block"
                      style={{ backgroundColor: mod.secondaryColor }}
                    />
                  </div>
                </div>
              </div>

              {/* Footer Specs */}
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-slate-800">
                <span>Stack: {mod.tech}</span>
                <span className="text-slate-300 font-semibold">{mod.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
