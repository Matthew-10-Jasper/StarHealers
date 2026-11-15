import React from 'react';
import {
  LayoutDashboard,
  Activity,
  UserCheck,
  ShieldAlert,
  History,
  Compass,
  Users,
  Layers,
  GitBranch,
  HeartPulse,
} from 'lucide-react';

export default function Sidebar({ activeTab, onSelectTab, alertsCount }) {
  const primaryNavItems = [
    {
      id: 'astronaut-dashboard',
      label: 'Astronaut Dashboard',
      icon: LayoutDashboard,
      badge: null,
      accent: 'cyan',
    },
    {
      id: 'vitals-monitoring',
      label: 'Module 1: Health Vitals',
      icon: Activity,
      badge: 'Core Vitals',
      accent: 'cyan',
    },
    {
      id: 'body-map',
      label: 'Module 2: Interactive Body Map',
      icon: HeartPulse,
      badge: 'SVG Anatomy',
      accent: 'cyan',
    },
    {
      id: 'triage-alerts',
      label: 'Module 3: Health Triage',
      icon: ShieldAlert,
      badge: alertsCount > 0 ? `${alertsCount} Active` : null,
      badgeColor: 'rose',
      accent: 'crimson',
    },
    {
      id: 'health-history',
      label: 'Telemetry History',
      icon: History,
      badge: 'Recharts',
      accent: 'cyan',
    },
  ];

  const secondaryNavItems = [
    {
      id: 'mission-overview',
      label: 'Mission Overview',
      icon: Compass,
      badge: null,
    },
    {
      id: 'crew-management',
      label: 'Crew Management',
      icon: Users,
      badge: '4 Crew',
    },
    {
      id: 'teammate-integrations',
      label: 'Teammate Modules',
      icon: Layers,
      badge: 'Shared Arch',
    },
  ];

  return (
    <aside className="w-64 shrink-0 glass-panel border-r border-slate-800/80 flex flex-col justify-between h-[calc(100vh-57px)]">
      {/* Top Nav Items */}
      <div className="p-3 space-y-6 overflow-y-auto">
        {/* Primary Assigned Modules */}
        <div>
          <div className="px-3 mb-2 flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
              Assigned Modules (Suba)
            </span>
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          </div>

          <nav className="space-y-1">
            {primaryNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition text-left ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-950/60 to-slate-900 border border-cyan-500/40 text-cyan-300 shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/50 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={`w-4 h-4 ${
                        isActive ? 'text-cyan-400' : 'text-slate-400'
                      }`}
                    />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${
                        item.badgeColor === 'rose'
                          ? 'bg-rose-950/60 border-rose-600/40 text-rose-300 font-semibold'
                          : 'bg-slate-800 border-slate-700 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Mission & Shared Application Views */}
        <div>
          <div className="px-3 mb-2">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
              Mission & Architecture
            </span>
          </div>

          <nav className="space-y-1">
            {secondaryNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition text-left ${
                    isActive
                      ? 'bg-slate-800/90 border border-slate-700 text-slate-100'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-slate-400" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 border border-slate-700 text-slate-400">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Footer: Git Branch & Integrity Status */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] font-mono">
          <div className="flex items-center gap-2 text-slate-300">
            <GitBranch className="w-3.5 h-3.5 text-cyan-400" />
            <span>branch:</span>
            <span className="text-cyan-400 font-bold">Suba</span>
          </div>
          <span className="w-2 h-2 rounded-full bg-emerald-400" title="Branch synced" />
        </div>
        <p className="text-[9px] font-mono text-center text-slate-400 mt-2">
          NASA-THEMED DEEP-SPACE MEDICAL AGENT
        </p>
      </div>
    </aside>
  );
}
