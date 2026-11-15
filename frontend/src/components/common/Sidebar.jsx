import React from 'react';
import {
  LayoutDashboard,
  Activity,
  ShieldAlert,
  History,
  Compass,
  Users,
  Layers,
  HeartPulse,
  LogOut,
  Radio,
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  onSelectTab,
  alertsCount,
  currentUser,
  onSignOut,
}) {
  const healthNavItems = [
    {
      id: 'astronaut-dashboard',
      label: 'Workspace Overview',
      icon: LayoutDashboard,
    },
    {
      id: 'vitals-monitoring',
      label: 'Crew Health',
      icon: Activity,
    },
    {
      id: 'body-map',
      label: 'Body Systems',
      icon: HeartPulse,
    },
    {
      id: 'triage-alerts',
      label: 'Health Alerts',
      icon: ShieldAlert,
      badge: alertsCount > 0 ? `${alertsCount}` : null,
      badgeColor: 'rose',
    },
    {
      id: 'health-history',
      label: 'Health History',
      icon: History,
    },
  ];

  const missionNavItems = [
    {
      id: 'mission-overview',
      label: 'Mission Overview',
      icon: Compass,
    },
    {
      id: 'crew-management',
      label: 'Crew Directory',
      icon: Users,
    },
    {
      id: 'teammate-integrations',
      label: 'Teammate Features',
      icon: Layers,
    },
  ];

  return (
    <aside className="w-64 shrink-0 glass-panel border-r border-slate-800/80 flex flex-col justify-between h-[calc(100vh-57px)]">
      {/* Navigation Sections */}
      <div className="p-3 space-y-6 overflow-y-auto">
        {/* Health Monitoring Section */}
        <div>
          <div className="px-3 mb-2 flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
              Health Workspace
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
          </div>

          <nav className="space-y-1">
            {healthNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition text-left cursor-pointer ${
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
                      className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                        item.badgeColor === 'rose'
                          ? 'bg-rose-950/80 border-rose-500/60 text-rose-300 font-bold'
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

        {/* Mission & Operations Section */}
        <div>
          <div className="px-3 mb-2">
            <span className="text-[10px] font-mono tracking-wider text-slate-400 uppercase">
              Operations & Crew
            </span>
          </div>

          <nav className="space-y-1">
            {missionNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition text-left cursor-pointer ${
                    isActive
                      ? 'bg-slate-800/90 border border-slate-700 text-slate-100'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-slate-400" />
                    <span>{item.label}</span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* User Session & Sign Out Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/70 border border-slate-800/90">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 font-bold text-xs flex items-center justify-center border border-cyan-500/30 shrink-0">
              {currentUser?.name ? currentUser.name[0] : 'S'}
            </div>
            <div className="min-w-0">
              <div className="text-xs font-semibold text-slate-200 truncate">
                {currentUser?.name || 'Dr. Sarah Chen'}
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                {currentUser?.callsign || 'Flight Surgeon'}
              </div>
            </div>
          </div>
          <button
            onClick={onSignOut}
            title="Sign Out to Welcome Screen"
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
