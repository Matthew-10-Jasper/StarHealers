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
        return 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.7))';
      case 'WARNING':
        return 'drop-shadow(0 0 6px rgba(245, 158, 11, 0.6))';
      case 'NORMAL':
        return 'drop-shadow(0 0 4px rgba(34, 197, 94, 0.4))';
      default:
        return 'none';
    }
  };

  const regions = [
    {
      id: 'brain',
      label: 'Brain & Eyes',
      cx: 150,
      cy: 62,
      r: 16,
      pulseX: 150,
      pulseY: 52,
    },
    {
      id: 'lungs',
      label: 'Respiratory (Lungs)',
      cx: 150,
      cy: 135,
      r: 22,
      pulseX: 132,
      pulseY: 135,
    },
    {
      id: 'heart',
      label: 'Cardiovascular (Heart)',
      cx: 160,
      cy: 142,
      r: 15,
      pulseX: 160,
      pulseY: 142,
    },
    {
      id: 'metabolic',
      label: 'Metabolic & Renal',
      cx: 150,
      cy: 210,
      r: 20,
      pulseX: 150,
      pulseY: 210,
    },
    {
      id: 'musculoskeletal',
      label: 'Musculoskeletal',
      cx: 150,
      cy: 310,
      r: 28,
      pulseX: 125,
      pulseY: 330,
    },
    {
      id: 'immune',
      label: 'Immune & Hematologic',
      cx: 185,
      cy: 105,
      r: 14,
      pulseX: 185,
      pulseY: 105,
    },
  ];

  return (
    <div className="relative flex flex-col items-center justify-center w-full py-4 select-none">
      <svg
        viewBox="0 0 300 460"
        className="w-full max-w-[320px] h-auto overflow-visible"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          {/* Subtle Grid Pattern inside silhouette */}
          <pattern id="bodyGrid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#1E293B" strokeWidth="0.5" />
          </pattern>

          {/* Gradients */}
          <linearGradient id="bodyGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0F172A" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#060913" stopOpacity="0.95" />
          </linearGradient>

          <linearGradient id="spineGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {/* Anatomical Human Body Silhouette (Precision Medical Vector Path) */}
        <g id="human-silhouette" className="transition-all duration-300">
          {/* Head & Neck */}
          <path
            d="M 150 24 
               C 134 24, 126 36, 126 54 
               C 126 68, 134 82, 140 88 
               L 142 98 
               C 130 102, 108 108, 98 120 
               C 92 128, 88 142, 85 170 
               C 83 192, 80 230, 78 250 
               C 76 266, 70 278, 68 285 
               C 66 290, 74 294, 78 288 
               C 82 280, 88 256, 92 235 
               L 98 232 
               L 98 200 
               C 102 215, 108 230, 114 250 
               C 118 262, 120 280, 120 300 
               L 122 340 
               C 122 370, 120 400, 118 435 
               C 117 444, 128 446, 132 438 
               C 136 430, 140 380, 144 330 
               L 150 270 
               L 156 330 
               C 160 380, 164 430, 168 438 
               C 172 446, 183 444, 182 435 
               C 180 400, 178 370, 178 340 
               L 180 300 
               C 180 280, 182 262, 186 250 
               C 192 230, 198 215, 202 200 
               L 202 232 
               L 208 235 
               C 212 256, 218 280, 222 288 
               C 226 294, 234 290, 232 285 
               C 230 278, 224 266, 222 250 
               C 220 230, 217 192, 215 170 
               C 212 142, 208 128, 202 120 
               C 192 108, 170 102, 158 98 
               L 160 88 
               C 166 82, 174 68, 174 54 
               C 174 36, 166 24, 150 24 Z"
            fill="url(#bodyGradient)"
            stroke="#1E293B"
            strokeWidth="1.5"
            className="filter drop-shadow-[0_4px_12px_rgba(0,0,0,0.6)]"
          />

          {/* Internal Anatomical Reference Lines (Central Axis & Ribcage Outline) */}
          <line x1="150" y1="95" x2="150" y2="265" stroke="url(#spineGradient)" strokeWidth="1.5" strokeDasharray="3 3" />
          
          {/* Subtle Ribcage lines */}
          <path d="M 134 125 C 142 122, 158 122, 166 125" fill="none" stroke="#1E293B" strokeWidth="1" />
          <path d="M 130 138 C 142 135, 158 135, 170 138" fill="none" stroke="#1E293B" strokeWidth="1" />
          <path d="M 132 152 C 142 150, 158 150, 168 152" fill="none" stroke="#1E293B" strokeWidth="1" />
          <path d="M 136 166 C 144 165, 156 165, 164 166" fill="none" stroke="#1E293B" strokeWidth="1" />
        </g>

        {/* Interactive Clickable Anatomical Regions */}

        {/* 1. BRAIN AND EYES */}
        <g
          id="region-brain"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('brain')}
          onMouseEnter={() => setHoveredRegion('brain')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Brain Contour Highlight */}
          <ellipse
            cx="150"
            cy="52"
            rx="18"
            ry="20"
            fill={selectedRegion === 'brain' ? 'rgba(0, 240, 255, 0.15)' : 'transparent'}
            stroke={selectedRegion === 'brain' ? '#00F0FF' : hoveredRegion === 'brain' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.5"
            strokeDasharray={selectedRegion === 'brain' ? 'none' : '2 2'}
          />
          {/* Node Indicator */}
          <circle
            cx="150"
            cy="52"
            r="6"
            fill={getStatusColor(regionStatuses?.brain)}
            className="transition-all duration-300"
            style={{ filter: getGlowFilter(regionStatuses?.brain) }}
          />
          <circle
            cx="150"
            cy="52"
            r="12"
            fill="none"
            stroke={getStatusColor(regionStatuses?.brain)}
            strokeWidth="1"
            opacity="0.4"
            className={regionStatuses?.brain === 'CRITICAL' ? 'animate-ping' : ''}
          />
          {/* Target Reticle if selected */}
          {selectedRegion === 'brain' && (
            <circle cx="150" cy="52" r="18" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
          )}
        </g>

        {/* 2. LUNGS (RESPIRATORY) */}
        <g
          id="region-lungs"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('lungs')}
          onMouseEnter={() => setHoveredRegion('lungs')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Left & Right Lung Silhouette Highlights */}
          <path
            d="M 132 120 C 122 125, 116 142, 120 162 C 124 168, 136 166, 140 155 Z"
            fill={selectedRegion === 'lungs' ? 'rgba(0, 240, 255, 0.12)' : 'transparent'}
            stroke={selectedRegion === 'lungs' ? '#00F0FF' : hoveredRegion === 'lungs' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.2"
          />
          <path
            d="M 168 120 C 178 125, 184 142, 180 162 C 176 168, 164 166, 160 155 Z"
            fill={selectedRegion === 'lungs' ? 'rgba(0, 240, 255, 0.12)' : 'transparent'}
            stroke={selectedRegion === 'lungs' ? '#00F0FF' : hoveredRegion === 'lungs' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.2"
          />
          {/* Indicator Node */}
          <circle
            cx="135"
            cy="142"
            r="6"
            fill={getStatusColor(regionStatuses?.lungs)}
            style={{ filter: getGlowFilter(regionStatuses?.lungs) }}
          />
          {regionStatuses?.lungs === 'CRITICAL' && (
            <circle cx="135" cy="142" r="14" fill="none" stroke="#EF4444" strokeWidth="1" className="animate-ping" />
          )}
        </g>

        {/* 3. HEART (CARDIOVASCULAR) */}
        <g
          id="region-heart"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('heart')}
          onMouseEnter={() => setHoveredRegion('heart')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          {/* Heart Vector Shape */}
          <path
            d="M 156 138 C 156 132, 164 130, 168 135 C 172 130, 180 132, 180 138 C 180 148, 168 156, 168 156 C 168 156, 156 148, 156 138 Z"
            fill={selectedRegion === 'heart' ? 'rgba(239, 68, 68, 0.2)' : 'transparent'}
            stroke={selectedRegion === 'heart' ? '#EF4444' : hoveredRegion === 'heart' ? '#F43F5E' : 'transparent'}
            strokeWidth="1.5"
          />
          <circle
            cx="168"
            cy="142"
            r="6"
            fill={getStatusColor(regionStatuses?.heart)}
            style={{ filter: getGlowFilter(regionStatuses?.heart) }}
          />
          <circle
            cx="168"
            cy="142"
            r="12"
            fill="none"
            stroke={getStatusColor(regionStatuses?.heart)}
            strokeWidth="1"
            opacity="0.5"
            className={regionStatuses?.heart === 'CRITICAL' ? 'animate-ping' : ''}
          />
          {selectedRegion === 'heart' && (
            <circle cx="168" cy="142" r="18" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
          )}
        </g>

        {/* 4. IMMUNE & LYMPHATIC (CLAVICULAR / NODAL) */}
        <g
          id="region-immune"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('immune')}
          onMouseEnter={() => setHoveredRegion('immune')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <circle
            cx="188"
            cy="104"
            r="5"
            fill={getStatusColor(regionStatuses?.immune)}
            style={{ filter: getGlowFilter(regionStatuses?.immune) }}
          />
          {selectedRegion === 'immune' && (
            <circle cx="188" cy="104" r="14" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="2 2" />
          )}
        </g>

        {/* 5. METABOLIC & RENAL (ABDOMEN / GLUCOSE / HYDRATION) */}
        <g
          id="region-metabolic"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('metabolic')}
          onMouseEnter={() => setHoveredRegion('metabolic')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <ellipse
            cx="150"
            cy="210"
            rx="22"
            ry="18"
            fill={selectedRegion === 'metabolic' ? 'rgba(0, 240, 255, 0.12)' : 'transparent'}
            stroke={selectedRegion === 'metabolic' ? '#00F0FF' : hoveredRegion === 'metabolic' ? '#38BDF8' : 'transparent'}
            strokeWidth="1.2"
          />
          <circle
            cx="150"
            cy="210"
            r="6"
            fill={getStatusColor(regionStatuses?.metabolic)}
            style={{ filter: getGlowFilter(regionStatuses?.metabolic) }}
          />
          {selectedRegion === 'metabolic' && (
            <circle cx="150" cy="210" r="18" fill="none" stroke="#00F0FF" strokeWidth="1.2" strokeDasharray="3 3" />
          )}
        </g>

        {/* 6. MUSCULOSKELETAL (LEGS / LIMBS / SPINE) */}
        <g
          id="region-musculoskeletal"
          className="cursor-pointer group"
          onClick={() => onSelectRegion('musculoskeletal')}
          onMouseEnter={() => setHoveredRegion('musculoskeletal')}
          onMouseLeave={() => setHoveredRegion(null)}
        >
          <circle
            cx="132"
            cy="330"
            r="6"
            fill={getStatusColor(regionStatuses?.musculoskeletal)}
            style={{ filter: getGlowFilter(regionStatuses?.musculoskeletal) }}
          />
          <circle
            cx="168"
            cy="330"
            r="6"
            fill={getStatusColor(regionStatuses?.musculoskeletal)}
            style={{ filter: getGlowFilter(regionStatuses?.musculoskeletal) }}
          />
          {selectedRegion === 'musculoskeletal' && (
            <path
              d="M 124 310 L 176 310 L 172 350 L 128 350 Z"
              fill="rgba(0, 240, 255, 0.1)"
              stroke="#00F0FF"
              strokeWidth="1.2"
              strokeDasharray="3 3"
            />
          )}
        </g>

        {/* Pointer Callout Lines for Active Selection */}
        {selectedRegion && (
          <g className="animate-in fade-in duration-200">
            {selectedRegion === 'brain' && (
              <>
                <line x1="168" y1="52" x2="245" y2="40" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="245" cy="40" r="2.5" fill="#00F0FF" />
                <text x="250" y="44" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600">
                  BRAIN & EYES
                </text>
              </>
            )}
            {selectedRegion === 'heart' && (
              <>
                <line x1="182" y1="142" x2="245" y2="135" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="245" cy="135" r="2.5" fill="#00F0FF" />
                <text x="250" y="139" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600">
                  HEART (CARDIO)
                </text>
              </>
            )}
            {selectedRegion === 'lungs' && (
              <>
                <line x1="120" y1="142" x2="45" y2="135" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="45" cy="135" r="2.5" fill="#00F0FF" />
                <text x="40" y="139" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600" textAnchor="end">
                  LUNGS (SPO2)
                </text>
              </>
            )}
            {selectedRegion === 'metabolic' && (
              <>
                <line x1="168" y1="210" x2="245" y2="210" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="245" cy="210" r="2.5" fill="#00F0FF" />
                <text x="250" y="214" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600">
                  METABOLIC
                </text>
              </>
            )}
            {selectedRegion === 'musculoskeletal' && (
              <>
                <line x1="174" y1="330" x2="245" y2="330" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="245" cy="330" r="2.5" fill="#00F0FF" />
                <text x="250" y="334" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600">
                  MUSCULOSKELETAL
                </text>
              </>
            )}
            {selectedRegion === 'immune' && (
              <>
                <line x1="194" y1="104" x2="245" y2="95" stroke="#00F0FF" strokeWidth="1" strokeDasharray="2 2" />
                <circle cx="245" cy="95" r="2.5" fill="#00F0FF" />
                <text x="250" y="99" fill="#00F0FF" fontSize="9" fontFamily="monospace" fontWeight="600">
                  IMMUNE / LYMPH
                </text>
              </>
            )}
          </g>
        )}
      </svg>

      {/* Floating System Legend below Body Map */}
      <div className="flex flex-wrap items-center justify-center gap-3 mt-4 text-[10px] font-mono text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400" /> Normal
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-400" /> Warning
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_6px_#f43f5e]" /> Critical
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-slate-500" /> No Data
        </span>
      </div>
    </div>
  );
}
