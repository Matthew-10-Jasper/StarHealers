import React from 'react';
import { Activity, ShieldAlert, HeartPulse, ChevronRight, UserCheck, Sparkles, Orbit, Radio } from 'lucide-react';
import heroImage from '../../assets/hero.png';

export default function WelcomeView({ onEnter, onQuickDemo }) {
  return (
    <div className="relative min-h-screen bg-[#060913] text-[#F8FAFC] flex flex-col justify-between overflow-hidden selection:bg-cyan-500 selection:text-black">
      {/* Background Ambient Glow & Starfield */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[700px] h-[700px] bg-gradient-to-b from-cyan-500/15 via-blue-600/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute top-1/3 -left-40 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-3xl" />
        <div className="absolute bottom-10 -right-40 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:32px_32px] opacity-40" />
      </div>

      {/* Top Header / Brand Bar */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/25 to-blue-600/20 border border-cyan-400/40 shadow-lg shadow-cyan-500/20">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-400"></span>
            </span>
          </div>
          <div>
            <span className="text-xl font-bold tracking-wider text-slate-100">
              STAR<span className="text-cyan-400">HEALERS</span>
            </span>
            <span className="block text-[11px] tracking-widest text-slate-400 font-mono uppercase">
              Aerospace Medical Platform
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-400">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>DEEP SPACE TELEMETRY ACTIVE</span>
          </div>
          <button
            onClick={onQuickDemo}
            className="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors px-3 py-1.5 rounded-lg border border-slate-800 hover:border-cyan-500/40 bg-slate-900/60"
          >
            Medical Demo Access
          </button>
        </div>
      </header>

      {/* Main Hero Section */}
      <main className="relative z-10 flex-1 max-w-7xl mx-auto px-6 py-8 flex flex-col lg:flex-row items-center justify-between gap-12 my-auto">
        {/* Left Column: Product Value Proposition */}
        <div className="flex-1 max-w-2xl text-center lg:text-left space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-medium tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Autonomous Aerospace Health & Life Support
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Intelligent Astronaut <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">
              Health Monitoring
            </span> & Medical Platform
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            Next-generation autonomous physiological telemetry, interactive holographic anatomical tracking,
            and continuous clinical triage engineered for long-duration deep-space exploration.
          </p>

          {/* Primary Action Buttons */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
            <button
              onClick={onEnter}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-base shadow-xl shadow-cyan-500/25 hover:shadow-cyan-400/35 transition-all duration-200 transform hover:-translate-y-0.5 active:translate-y-0 cursor-pointer"
            >
              <span>Enter StarHealers</span>
              <ChevronRight className="w-5 h-5 text-slate-950" />
            </button>

            <button
              onClick={onQuickDemo}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-slate-900/90 hover:bg-slate-800/90 text-slate-200 font-semibold text-sm border border-slate-800 hover:border-slate-700 transition-all duration-200"
            >
              <UserCheck className="w-4 h-4 text-cyan-400" />
              <span>Launch Demo Profile</span>
            </button>
          </div>

          {/* Trust & Spec Markers */}
          <div className="pt-6 grid grid-cols-3 gap-4 border-t border-slate-800/80 text-left">
            <div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-cyan-400">Continuous</div>
              <div className="text-xs text-slate-400 mt-0.5">Biometric Telemetry</div>
            </div>
            <div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-slate-200">5-Zone</div>
              <div className="text-xs text-slate-400 mt-0.5">Anatomical Mapping</div>
            </div>
            <div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-amber-400">&lt; 250ms</div>
              <div className="text-xs text-slate-400 mt-0.5">Triage Latency</div>
            </div>
          </div>
        </div>

        {/* Right Column: Premium Visual Showcase */}
        <div className="flex-1 w-full max-w-lg lg:max-w-xl">
          <div className="relative group">
            {/* Ambient Background Halo */}
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/30 to-blue-600/30 rounded-3xl blur-2xl opacity-60 group-hover:opacity-80 transition duration-500" />

            <div className="relative rounded-2xl bg-slate-900/90 border border-slate-800/90 p-5 shadow-2xl backdrop-blur-xl">
              {/* Product Visual Mockup */}
              <div className="relative rounded-xl overflow-hidden aspect-[4/3] bg-gradient-to-b from-slate-950 via-[#0a1122] to-slate-950 flex items-center justify-center border border-slate-800/60">
                <img
                  src={heroImage}
                  alt="StarHealers Aerospace Health Visual"
                  className="w-full h-full object-cover object-center opacity-85 hover:scale-105 transition-transform duration-700"
                />

                {/* Overlay Floating Status Badge */}
                <div className="absolute top-4 left-4 flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800/90 backdrop-blur-md">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs font-mono font-medium text-slate-200">CREW HEALTH OPTIMAL</span>
                </div>

                {/* Floating Metric Preview */}
                <div className="absolute bottom-4 right-4 flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-950/85 border border-cyan-500/30 backdrop-blur-md">
                  <HeartPulse className="w-4 h-4 text-cyan-400 animate-pulse" />
                  <div>
                    <div className="text-[10px] font-mono text-slate-400">TELEMETRY LINK</div>
                    <div className="text-xs font-mono font-bold text-cyan-300">99.8% STABLE</div>
                  </div>
                </div>
              </div>

              {/* Three Feature Highlights Under Visual */}
              <div className="mt-4 grid grid-cols-3 gap-2.5">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/70 text-center">
                  <Activity className="w-4 h-4 text-cyan-400 mx-auto mb-1.5" />
                  <div className="text-[11px] font-semibold text-slate-200">Crew Health</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Live Vitals</div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/70 text-center">
                  <Orbit className="w-4 h-4 text-sky-400 mx-auto mb-1.5" />
                  <div className="text-[11px] font-semibold text-slate-200">Body Systems</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Anatomy Model</div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/70 text-center">
                  <ShieldAlert className="w-4 h-4 text-amber-400 mx-auto mb-1.5" />
                  <div className="text-[11px] font-semibold text-slate-200">Health Alerts</div>
                  <div className="text-[10px] text-slate-400 mt-0.5">Automated Triage</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div>
          StarHealers &bull; Intelligent Astronaut Health Monitoring and Medical Support Platform
        </div>
        <div className="flex items-center gap-6">
          <span className="hover:text-slate-400 transition-colors">Privacy Policy</span>
          <span className="hover:text-slate-400 transition-colors">Operational Protocols</span>
          <span className="hover:text-slate-400 transition-colors">Medical System Specs</span>
        </div>
      </footer>
    </div>
  );
}
