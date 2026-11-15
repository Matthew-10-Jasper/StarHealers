import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';

export default function SeverityBadge({ severity, size = 'md', showIcon = true }) {
  const sev = (severity || 'NO_DATA').toUpperCase();

  const configs = {
    NORMAL: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400',
      label: 'NORMAL',
      icon: CheckCircle2,
      dot: 'bg-emerald-400',
    },
    WARNING: {
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
      label: 'WARNING',
      icon: AlertTriangle,
      dot: 'bg-amber-400',
    },
    CRITICAL: {
      bg: 'bg-rose-500/15',
      border: 'border-rose-500/40',
      text: 'text-rose-400',
      label: 'CRITICAL',
      icon: AlertCircle,
      dot: 'bg-rose-500 shadow-[0_0_8px_#f43f5e]',
    },
    NO_DATA: {
      bg: 'bg-slate-700/20',
      border: 'border-slate-600/30',
      text: 'text-slate-400',
      label: 'NO DATA',
      icon: HelpCircle,
      dot: 'bg-slate-400',
    },
  };

  const current = configs[sev] || configs.NO_DATA;
  const Icon = current.icon;

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-full border ${current.bg} ${current.border} ${current.text} ${sizeClasses}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`} />
      {showIcon && <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />}
      <span>{current.label}</span>
    </span>
  );
}
