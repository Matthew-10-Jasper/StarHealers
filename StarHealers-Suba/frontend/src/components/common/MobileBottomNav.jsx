import React from 'react';
import { Compass, Users, Activity, HeartPulse, ShieldAlert } from 'lucide-react';

export default function MobileBottomNav({ activeTab, onSelectTab, alertsCount }) {
  const items = [
    {
      id: 'mission-overview',
      label: 'Home',
      icon: Compass,
    },
    {
      id: 'crew-management',
      label: 'Crew',
      icon: Users,
    },
    {
      id: 'vitals-monitoring',
      label: 'Health',
      icon: Activity,
    },
    {
      id: 'body-map',
      label: 'Body',
      icon: HeartPulse,
    },
    {
      id: 'triage-alerts',
      label: 'Alerts',
      icon: ShieldAlert,
      badge: alertsCount > 0 ? alertsCount : null,
    },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#060913]/95 backdrop-blur-xl border-t border-slate-800/90 px-2 py-1.5 flex items-center justify-around safe-area-inset-bottom">
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;

        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`relative flex flex-col items-center justify-center py-1 px-3 rounded-xl transition cursor-pointer ${
              isActive
                ? 'text-cyan-400 font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="relative">
              <Icon className={`w-5 h-5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
              {item.badge && (
                <span className="absolute -top-1 -right-2 px-1.5 py-0.2 rounded-full text-[9px] font-bold bg-rose-600 text-white animate-pulse">
                  {item.badge}
                </span>
              )}
            </div>
            <span className="text-[10px] tracking-tight mt-0.5 font-sans">
              {item.label}
            </span>
            {isActive && (
              <span className="w-1 h-1 rounded-full bg-cyan-400 mt-0.5" />
            )}
          </button>
        );
      })}
    </nav>
  );
}
