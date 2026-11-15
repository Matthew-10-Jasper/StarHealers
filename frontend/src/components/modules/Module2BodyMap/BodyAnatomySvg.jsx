import React, { useState } from 'react';

export default function BodyAnatomySvg({
  regionStatuses,
  selectedRegion,
  onSelectRegion,
  viewMode = 'front', // 'front' | 'back'
}) {
  const [hoveredRegion, setHoveredRegion] = useState(null);

  const getStatusColor = (status) => {
    switch (status) {
      case 'CRITICAL':
        return '#EF4444'; // Red
      case 'WARNING':
        return '#F59E0B'; // Amber
      case 'NORMAL':
        return '#22C55E'; // Green
      default:
        return '#64748B'; // Grey (No Data)
    }
  };

  const getGlowFilter = (status) => {
    switch (status) {
      case 'CRITICAL':
        return 'drop-shadow(0 0 10px rgba(239, 68, 68, 0.9))';
      case 'WARNING':
        return 'drop-shadow(0 0 8px rgba(245, 158, 11, 0.8))';
      case 'NORMAL':
        return 'drop-shadow(0 0 5px rgba(34, 197, 94, 0.5))';
      default:
        return 'none';
    }
  };

  const isBack = viewMode === 'back';

  return (
    <div className="relative flex flex-col items-center justify-center w-full py-2 select-none">
      {/* Sci-Fi Ambient Diagnostic Rings & Radial HUD Backdrop */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
        <div className="w-72 h-72 rounded-full border border-cyan-500/10 animate-[spin_60s_linear_infinite]" />
        <div className="absolute w-88 h-88 rounded-full border border-dashed border-slate-700/20" />
      </div>

      <svg
        viewBox="0 0 320 480"
        className="w-full max-w-[340px] h-auto overflow-visible relative z-10"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Hologram Grid Pattern */}
          <pattern id="holoGrid" width="12" height="12" patternUnits="userSpaceOnUse">
            <path d="M 12 0 L 0 0 0 12" fill="none" stroke="#00F0FF" strokeWidth="0.3" opacity="0.15" />
          </pattern>

          {/* Premium Body Surface Gradient */}
          <linearGradient id="premiumBodyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0F172A" stopOpacity="0.95" />
            <stop offset="35%" stopColor="#111C35" stopOpacity="0.9" />
            <stop offset="70%" stopColor="#0B132B" stopOpacity="0.92" />
            <stop offset="100%" stopColor="#060913" stopOpacity="0.98" />
          </linearGradient>

          {/* Neon Spine Gradient */}
          <linearGradient id="spineNeon" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#3B82F6" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.4" />
          </linearGradient>

          {/* Neural Mesh Gradient */}
          <linearGradient id="neuralGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#D946EF" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {/* 1. ANATOMICAL HUMAN BODY SILHOUETTE (Medical Vector Geometry) */}
        <g id="body-chassis" className="transition-all duration-300">
          {/* Main Anatomical Silhouette */}
          <path
            d="M 160 26 
               C 142 26, 134 38, 134 58 
               C 134 72, 142 86, 148 92 
               L 150 102 
               C 138 106, 114 112, 104 125 
               C 97 134, 93 148, 90 176 
               C 87 200, 84 238, 82 258 
               C 80 274, 73 286, 71 294 
               C 69 299, 78 303, 82 297 
               C 87 289, 93 264, 97 242 
               L 104 239 
               L 104 205 
               C 108 221, 115 237, 121 258 
               C 125 271, 127 289, 127 310 
               L 129 352 
               C 129 384, 127 416, 125 452 
               C 124 461, 136 463, 140 455 
               C 144 447, 149 395, 153 342 
               L 160 280 
               L 167 342 
               C 171 395, 176 447, 180 455 
               C 184 463, 196 461, 195 452 
               C 193 416, 191 384, 191 352 
               L 193 310 
               C 193 289, 195 271, 199 258 
               C 205 237, 212 221, 216 205 
               L 216 239 
               L 223 242 
               C 227 264, 233 289, 238 297 
               C 242 303, 251 299, 249 294 
               C 247 286, 240 274, 238 258 
               C 236 238, 233 200, 230 176 
               C 227 148, 223 134, 216 125 
               C 206 112, 182 106, 170 102 
               L 172 92 
               C 178 86, 186 72, 186 58 
               C 186 38, 178 26, 160 26 Z"
            fill="url(#premiumBodyGrad)"
            stroke="#1E293B"
            strokeWidth="1.8"
            className="filter drop-shadow-[0_8px_20px_rgba(0,0,0,0.8)]"
          />

          {/* Hologram Overlay Texture */}
          <path
            d="M 160 26 
               C 142 26, 134 38, 134 58 
               C 134 72, 142 86, 148 92 
               L 150 102 
               C 138 106, 114 112, 104 125 
               C 97 134, 93 148, 90 176 
               C 87 200, 84 238, 82 258 
               C 80 274, 73 286, 71 294 
               C 69 299, 78 303, 82 297 
               C 87 289, 93 264, 97 242 
               L 104 239 
               L 104 205 
               C 108 221, 115 237, 121 258 
               C 125 271, 127 289, 127 310 
               L 129 352 
               C 129 384, 127 416, 125 452 
               C 124 461, 136 463, 140 455 
               C 144 447, 149 395, 153 342 
               L 160 280 
               L 167 342 
               C 171 395, 176 447, 180 455 
               C 184 463, 196 461, 195 452 
               C 193 416, 191 384, 191 352 
               L 193 310 
               C 193 289, 195 271, 199 258 
               C 205 237, 212 221, 216 205 
               L 216 239 
               L 223 242 
               C 227 264, 233 289, 238 297 
               C 242 303, 251 299, 249 294 
               C 247 286, 240 274, 238 258 
               C 236 238, 233 200, 230 176 
               C 227 148, 223 134, 216 125 
               C 206 112, 182 106, 170 102 
               L 172 92 
               C 178 86, 186 72, 186 58 
               C 186 38, 178 26, 160 26 Z"
            fill="url(#holoGrid)"
            opacity="0.75"
          />

          {/* Central Spinal Column (Glowing Vertebral Core) */}
          <line
            x1="160"
            y1="98"
            x2="160"
            y2="280"
            stroke="url(#spineNeon)"
            strokeWidth={isBack ? "3" : "1.5"}
            strokeDasharray={isBack ? "none" : "3 3"}
            opacity={isBack ? "0.9" : "0.5"}
          />
          {/* Vertebral disc markers */}
          {[115, 130, 145, 160, 175, 190, 205, 220, 235, 250].map((y) => (
            <circle key={y} cx="160" cy={y} r={isBack ? "2.5" : "1.5"} fill="#00F0FF" opacity={isBack ? "0.8" : "0.4"} />
          ))}

          {/* Clavicle & Shoulder Girdles */}
          <path d="M 124 110 C 142 118, 155 118, 160 118 C 165 118, 178 118, 196 110" fill="none" stroke="#334155" strokeWidth="1.2" opacity="0.6" />

          {/* Ribcage Contours (Anterior) */}
          {!isBack && (
            <g id="ribcage" opacity="0.45" stroke="#334155" strokeWidth="1" fill="none">
              <path d="M 142 132 C 150 128, 170 128, 178 132" />
              <path d="M 138 146 C 150 142, 170 142, 182 146" />
              <path d="M 140 160 C 150 156, 170 156, 180 160" />
              <path d="M 144 174 C 152 171, 168 171, 176 174" />
            </g>
          )}

          {/* Scapula & Dorsal Contours (Posterior) */}
          {isBack && (
            <g id="dorsal" opacity="0.6" stroke="#475569" strokeWidth="1.2" fill="none">
              <path d="M 130 130 C 138 145, 138 165, 145 170" />
              <path d="M 190 130 C 182 145, 182 165, 175 170" />
            </g>
          )}

          {/* Pelvis & Hip Joints */}
          <ellipse cx="140" cy="285" rx="8" ry="5" fill="none" stroke="#334155" strokeWidth="1" opacity="0.5" />
          <ellipse cx="180" cy="285" rx="8" ry="5" fill="none" stroke="#334155" strokeWidth="1" opacity="0.5" />

          {/* Knee & Ankle Bio-Nodes */}
          <circle cx="140" cy="370" r="3" fill="#1E293B" stroke="#00F0FF" strokeWidth="0.8" opacity="0.6" />
          <circle cx="180" cy="370" r="3" fill="#1E293B" stroke="#00F0FF" strokeWidth="0.8" opacity="0.6" />
          <circle cx="134" cy="442" r="2.5" fill="#1E293B" stroke="#00F0FF" strokeWidth="0.8" opacity="0.5" />
          <circle cx="186" cy="442" r="2.5" fill="#1E293B" stroke="#00F0FF" strokeWidth="0.8" opacity="0.5" />
        </g>

        {/* 2. INTERACTIVE CLINICAL BODY REGIONS */}

        {/* REGION 1: BRAIN & EYES (Neuro-Cognitive) */}
        <g
          id="system-brain"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('brain')}
          onMouseEnter={() => setHoveredRegion('brain')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Neural Cortex Lattice */}
          <ellipse
            cx="160"
            cy="56"
            rx="19"
            ry="21"
            fill={selectedRegion === 'brain' ? 'rgba(0, 240, 255, 0.18)' : hoveredRegion === 'brain' ? 'rgba(0, 240, 255, 0.08)' : 'transparent'}
            stroke={selectedRegion === 'brain' ? '#00F0FF' : hoveredRegion === 'brain' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.6"
            strokeDasharray={selectedRegion === 'brain' ? 'none' : '3 3'}
          />

          {/* Brain Inner Neural Curves */}
          <path
            d="M 152 46 C 156 42, 164 42, 168 46 C 172 50, 168 56, 160 56 C 152 56, 148 50, 152 46 Z"
            fill="none"
            stroke={getStatusColor(regionStatuses?.brain)}
            strokeWidth="1"
            opacity="0.7"
          />

          {/* Node Core */}
          <circle
            cx="160"
            cy="56"
            r="6.5"
            fill={getStatusColor(regionStatuses?.brain)}
            style={{ filter: getGlowFilter(regionStatuses?.brain) }}
          />
          {/* Pulse Ring */}
          <circle
            cx="160"
            cy="56"
            r="13"
            fill="none"
            stroke={getStatusColor(regionStatuses?.brain)}
            strokeWidth="1.2"
            opacity="0.4"
            className={regionStatuses?.brain === 'CRITICAL' ? 'animate-ping' : ''}
          />
          {/* Selected Reticle */}
          {selectedRegion === 'brain' && (
            <g className="animate-in fade-in duration-200">
              <circle cx="160" cy="56" r="22" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
              <line x1="160" y1="31" x2="160" y2="35" stroke="#00F0FF" strokeWidth="1.5" />
              <line x1="160" y1="77" x2="160" y2="81" stroke="#00F0FF" strokeWidth="1.5" />
              <line x1="135" y1="56" x2="139" y2="56" stroke="#00F0FF" strokeWidth="1.5" />
              <line x1="181" y1="56" x2="185" y2="56" stroke="#00F0FF" strokeWidth="1.5" />
            </g>
          )}
        </g>

        {/* REGION 2: LUNGS (Pulmonary Respiratory) */}
        <g
          id="system-lungs"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('lungs')}
          onMouseEnter={() => setHoveredRegion('lungs')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Left & Right Bronchial Lobes */}
          <path
            d="M 142 128 C 130 132, 122 150, 126 172 C 131 180, 145 178, 150 166 Z"
            fill={selectedRegion === 'lungs' ? 'rgba(0, 240, 255, 0.16)' : hoveredRegion === 'lungs' ? 'rgba(0, 240, 255, 0.08)' : 'transparent'}
            stroke={selectedRegion === 'lungs' ? '#00F0FF' : hoveredRegion === 'lungs' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.4"
          />
          <path
            d="M 178 128 C 190 132, 198 150, 194 172 C 189 180, 175 178, 170 166 Z"
            fill={selectedRegion === 'lungs' ? 'rgba(0, 240, 255, 0.16)' : hoveredRegion === 'lungs' ? 'rgba(0, 240, 255, 0.08)' : 'transparent'}
            stroke={selectedRegion === 'lungs' ? '#00F0FF' : hoveredRegion === 'lungs' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.4"
          />
          {/* Pulmonary Node */}
          <circle
            cx="145"
            cy="152"
            r="6.5"
            fill={getStatusColor(regionStatuses?.lungs)}
            style={{ filter: getGlowFilter(regionStatuses?.lungs) }}
          />
          {regionStatuses?.lungs === 'CRITICAL' && (
            <circle cx="145" cy="152" r="15" fill="none" stroke="#EF4444" strokeWidth="1.5" className="animate-ping" />
          )}
        </g>

        {/* REGION 3: HEART (Cardiovascular Telemetry) */}
        <g
          id="system-heart"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('heart')}
          onMouseEnter={() => setHoveredRegion('heart')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Anatomical Cardiac Contour */}
          <path
            d="M 166 142 C 166 135, 175 132, 180 138 C 185 132, 194 135, 194 142 C 194 154, 180 163, 180 163 C 180 163, 166 154, 166 142 Z"
            fill={selectedRegion === 'heart' ? 'rgba(239, 68, 68, 0.25)' : hoveredRegion === 'heart' ? 'rgba(239, 68, 68, 0.15)' : 'transparent'}
            stroke={selectedRegion === 'heart' ? '#EF4444' : hoveredRegion === 'heart' ? '#F43F5E' : 'transparent'}
            strokeWidth="1.6"
          />
          {/* Glowing Sinus Node */}
          <circle
            cx="180"
            cy="147"
            r="7"
            fill={getStatusColor(regionStatuses?.heart)}
            style={{ filter: getGlowFilter(regionStatuses?.heart) }}
          />
          <circle
            cx="180"
            cy="147"
            r="14"
            fill="none"
            stroke={getStatusColor(regionStatuses?.heart)}
            strokeWidth="1.2"
            opacity="0.5"
            className={regionStatuses?.heart === 'CRITICAL' ? 'animate-ping' : ''}
          />
          {selectedRegion === 'heart' && (
            <g className="animate-in fade-in duration-200">
              <circle cx="180" cy="147" r="22" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
              <line x1="180" y1="122" x2="180" y2="126" stroke="#00F0FF" strokeWidth="1.5" />
              <line x1="180" y1="168" x2="180" y2="172" stroke="#00F0FF" strokeWidth="1.5" />
            </g>
          )}
        </g>

        {/* REGION 4: IMMUNE & LYMPHATIC (Clavicular / Nodes) */}
        <g
          id="system-immune"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('immune')}
          onMouseEnter={() => setHoveredRegion('immune')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <circle
            cx="198"
            cy="114"
            r="5.5"
            fill={getStatusColor(regionStatuses?.immune)}
            style={{ filter: getGlowFilter(regionStatuses?.immune) }}
          />
          {selectedRegion === 'immune' && (
            <circle cx="198" cy="114" r="14" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="2 2" />
          )}
        </g>

        {/* REGION 5: METABOLIC & RENAL (Abdomen / Glycemic / Hydration) */}
        <g
          id="system-metabolic"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('metabolic')}
          onMouseEnter={() => setHoveredRegion('metabolic')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <ellipse
            cx="160"
            cy="222"
            rx="24"
            ry="20"
            fill={selectedRegion === 'metabolic' ? 'rgba(0, 240, 255, 0.16)' : hoveredRegion === 'metabolic' ? 'rgba(0, 240, 255, 0.08)' : 'transparent'}
            stroke={selectedRegion === 'metabolic' ? '#00F0FF' : hoveredRegion === 'metabolic' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.4"
          />
          <circle
            cx="160"
            cy="222"
            r="6.5"
            fill={getStatusColor(regionStatuses?.metabolic)}
            style={{ filter: getGlowFilter(regionStatuses?.metabolic) }}
          />
          {selectedRegion === 'metabolic' && (
            <circle cx="160" cy="222" r="20" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
          )}
        </g>

        {/* REGION 6: MUSCULOSKELETAL (Limbs, Biomechanics, Spine) */}
        <g
          id="system-musculoskeletal"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('musculoskeletal')}
          onMouseEnter={() => setHoveredRegion('musculoskeletal')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <circle
            cx="140"
            cy="345"
            r="6.5"
            fill={getStatusColor(regionStatuses?.musculoskeletal)}
            style={{ filter: getGlowFilter(regionStatuses?.musculoskeletal) }}
          />
          <circle
            cx="180"
            cy="345"
            r="6.5"
            fill={getStatusColor(regionStatuses?.musculoskeletal)}
            style={{ filter: getGlowFilter(regionStatuses?.musculoskeletal) }}
          />
          {selectedRegion === 'musculoskeletal' && (
            <path
              d="M 132 325 L 188 325 L 184 365 L 136 365 Z"
              fill="rgba(0, 240, 255, 0.12)"
              stroke="#00F0FF"
              strokeWidth="1.4"
              strokeDasharray="3 3"
            />
          )}
        </g>

        {/* 3. SCI-FI HUD CALLOUT POINTERS */}
        {selectedRegion && (
          <g className="animate-in fade-in duration-200">
            {selectedRegion === 'brain' && (
              <>
                <line x1="179" y1="56" x2="260" y2="44" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="260" cy="44" r="2.5" fill="#00F0FF" />
                <text x="266" y="47" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700">
                  BRAIN & EYES
                </text>
              </>
            )}
            {selectedRegion === 'heart' && (
              <>
                <line x1="194" y1="147" x2="260" y2="140" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="260" cy="140" r="2.5" fill="#00F0FF" />
                <text x="266" y="143" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700">
                  HEART (CARDIO)
                </text>
              </>
            )}
            {selectedRegion === 'lungs' && (
              <>
                <line x1="126" y1="152" x2="48" y2="142" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="48" cy="142" r="2.5" fill="#00F0FF" />
                <text x="42" y="145" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700" textAnchor="end">
                  LUNGS (SPO2)
                </text>
              </>
            )}
            {selectedRegion === 'metabolic' && (
              <>
                <line x1="184" y1="222" x2="260" y2="222" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="260" cy="222" r="2.5" fill="#00F0FF" />
                <text x="266" y="225" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700">
                  METABOLIC
                </text>
              </>
            )}
            {selectedRegion === 'musculoskeletal' && (
              <>
                <line x1="186" y1="345" x2="260" y2="345" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="260" cy="345" r="2.5" fill="#00F0FF" />
                <text x="266" y="348" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700">
                  MUSCULOSKELETAL
                </text>
              </>
            )}
            {selectedRegion === 'immune' && (
              <>
                <line x1="204" y1="114" x2="260" y2="105" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="260" cy="105" r="2.5" fill="#00F0FF" />
                <text x="266" y="108" fill="#00F0FF" fontSize="9.5" fontFamily="monospace" fontWeight="700">
                  IMMUNE / LYMPH
                </text>
              </>
            )}
          </g>
        )}
      </svg>

      {/* Floating System Legend below Body Map */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-3 text-[10px] font-mono text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(34,197,94,0.6)]" /> Normal
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-[0_0_6px_rgba(245,158,11,0.6)]" /> Warning
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(239,68,68,0.8)] animate-pulse" /> Critical
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-500" /> No Data
        </span>
      </div>
    </div>
  );
}
