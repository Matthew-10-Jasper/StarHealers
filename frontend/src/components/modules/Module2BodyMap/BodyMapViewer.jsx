import React, { useState, useEffect } from 'react';
import BodyAnatomySvg from './BodyAnatomySvg';
import RegionDetailPanel from './RegionDetailPanel';
import { BODY_REGIONS_CONFIG } from '../../../data/mockData';
import { getBodyRegionDetail, getBodyMap } from '../../../services/api';
import { HeartPulse, Eye, RotateCw, Activity, ShieldCheck, RefreshCw } from 'lucide-react';

export default function BodyMapViewer({
  astronaut,
  readings,
  alerts,
  onNavigateToMetric,
}) {
  const [selectedRegion, setSelectedRegion] = useState('heart');
  const [viewMode, setViewMode] = useState('front');
  const [backendRegionData, setBackendRegionData] = useState(null);
  const [isLoadingRegion, setIsLoadingRegion] = useState(false);

  const regionStatuses = astronaut.bodyRegionStatus || {};

  // Fetch live detailed telemetry for the selected organ region
  useEffect(() => {
    let isMounted = true;
    async function fetchRegionData() {
      setIsLoadingRegion(true);
      try {
        const data = await getBodyRegionDetail(astronaut.id, selectedRegion);
        if (isMounted && data) {
          setBackendRegionData(data);
        }
      } catch (err) {
        console.warn(`Could not load backend body map for ${selectedRegion}:`, err);
      } finally {
        if (isMounted) setIsLoadingRegion(false);
      }
    }
    fetchRegionData();
    return () => {
      isMounted = false;
    };
  }, [astronaut.id, selectedRegion]);

  return (
    <div className="space-y-6">
      {/* Module 2 Header */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <h2 className="text-lg font-bold text-slate-100 font-sans tracking-wide">
              Module 2: Interactive Human Body Map
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/40">
              SVG Anatomical Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Interactive anatomical telemetry correlation connecting live biometric signals to organ systems.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-2">
          <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
            <button
              onClick={() => setViewMode('front')}
              className={`px-3 py-1 rounded transition ${
                viewMode === 'front'
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Anterior (Front)
            </button>
            <button
              onClick={() => setViewMode('back')}
              className={`px-3 py-1 rounded transition ${
                viewMode === 'back'
                  ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Posterior (Back)
            </button>
          </div>
        </div>
      </div>

      {/* Main Split Layout: Anatomical Model on Left, Detail Panel on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Anatomical SVG Viewer */}
        <div className="lg:col-span-6 glass-panel rounded-xl p-6 border border-slate-800 flex flex-col items-center justify-between relative overflow-hidden">
          {/* Subtle Background Grid & Medical Radar Scanline */}
          <div className="absolute inset-0 space-grid-bg opacity-30 pointer-events-none" />
          
          {/* Active Astronaut Quick Pill */}
          <div className="w-full flex items-center justify-between z-10 mb-2 pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-slate-400">TARGET:</span>
              <span className="text-slate-100 font-bold">{astronaut.name}</span>
              <span className="text-cyan-400">({astronaut.id})</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
              {isLoadingRegion && <RefreshCw className="w-3 h-3 text-cyan-400 animate-spin" />}
              <span>VIEW: {viewMode.toUpperCase()}</span>
            </div>
          </div>

          {/* SVG Body Map */}
          <div className="z-10 w-full flex justify-center py-2">
            <BodyAnatomySvg
              regionStatuses={regionStatuses}
              selectedRegion={selectedRegion}
              onSelectRegion={setSelectedRegion}
              viewMode={viewMode}
            />
          </div>

          {/* System Quick Selection Bar */}
          <div className="w-full z-10 pt-4 border-t border-slate-800/80">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-2 text-center">
              CLICKABLE ANATOMICAL SUBSYSTEMS
            </span>
            <div className="grid grid-cols-3 gap-2">
              {Object.keys(BODY_REGIONS_CONFIG).map((key) => {
                const reg = BODY_REGIONS_CONFIG[key];
                const status = regionStatuses[key] || 'NO_DATA';
                const isSelected = selectedRegion === key;

                return (
                  <button
                    key={key}
                    onClick={() => setSelectedRegion(key)}
                    className={`p-2 rounded-lg text-left border transition text-xs font-mono flex items-center justify-between ${
                      isSelected
                        ? 'bg-cyan-950/70 border-cyan-400 text-cyan-300 shadow-cyan-glow'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    <span className="truncate">{reg.label.split(' ')[0]}</span>
                    <span
                      className={`w-2 h-2 rounded-full shrink-0 ml-1 ${
                        status === 'CRITICAL'
                          ? 'bg-rose-500'
                          : status === 'WARNING'
                          ? 'bg-amber-400'
                          : status === 'NORMAL'
                          ? 'bg-emerald-400'
                          : 'bg-slate-500'
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Region Details, Biometrics, and Active Alerts */}
        <div className="lg:col-span-6">
          <RegionDetailPanel
            regionId={selectedRegion}
            regionConfig={backendRegionData || BODY_REGIONS_CONFIG[selectedRegion]}
            regionStatus={backendRegionData?.status || regionStatuses[selectedRegion]}
            astronaut={astronaut}
            readings={backendRegionData?.currentReadings || readings}
            alerts={backendRegionData?.activeAlerts || alerts}
            onNavigateToMetric={onNavigateToMetric}
          />
        </div>
      </div>
    </div>
  );
}
