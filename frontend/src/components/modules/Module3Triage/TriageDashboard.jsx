import React, { useState } from 'react';
import SeverityBadge from '../../common/SeverityBadge';
import AlertDetailModal from './AlertDetailModal';
import RuleConfigModal from './RuleConfigModal';
import {
  ShieldAlert,
  AlertTriangle,
  Sliders,
  Filter,
  Search,
  CheckCircle,
  FileText,
  Clock,
  User,
  Activity,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function TriageDashboard({
  alerts,
  astronauts,
  selectedAstronaut,
  onSelectAstronaut,
  onAcknowledgeAlert,
}) {
  const [activeTab, setActiveTab] = useState('ACTIVE'); // 'ACTIVE' | 'RESOLVED' | 'ALL'
  const [severityFilter, setSeverityFilter] = useState('ALL'); // 'ALL' | 'CRITICAL' | 'WARNING' | 'NO_DATA'
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterBySelectedAstronautOnly, setFilterBySelectedAstronautOnly] = useState(false);

  // Filter alerts based on user selections
  const filteredAlerts = alerts.filter((alert) => {
    // Status tab filter
    if (activeTab !== 'ALL' && alert.status !== activeTab) return false;

    // Severity filter
    if (severityFilter !== 'ALL' && alert.severity !== severityFilter) return false;

    // Astronaut filter
    if (filterBySelectedAstronautOnly && alert.astronautId !== selectedAstronaut.id) return false;

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = alert.title.toLowerCase().includes(q);
      const matchReason = alert.triggerReason?.toLowerCase().includes(q);
      const matchAstro = alert.astronautId.toLowerCase().includes(q);
      if (!matchTitle && !matchReason && !matchAstro) return false;
    }

    return true;
  });

  const handleOpenAlert = (alert) => {
    setSelectedAlert(alert);
    setIsDetailModalOpen(true);
  };

  const activeAlertsCount = alerts.filter((a) => a.status === 'ACTIVE').length;
  const criticalCount = alerts.filter((a) => a.status === 'ACTIVE' && a.severity === 'CRITICAL').length;
  const warningCount = alerts.filter((a) => a.status === 'ACTIVE' && a.severity === 'WARNING').length;

  return (
    <div className="space-y-6">
      {/* Module 3 Header (Palette 4: Crimson & Amber) */}
      <div className="glass-panel rounded-xl p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
            <h2 className="text-lg font-bold text-slate-100 font-sans tracking-wide">
              Module 3: Intelligent Health Triage Engine
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800/40">
              Rule-Based Alert & Triage
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Explainable rule-based clinical decision support and multi-signal physiological risk evaluation.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsConfigModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 hover:border-slate-500 text-xs font-mono text-slate-200 transition"
          >
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span>Configure Rule Thresholds</span>
          </button>
        </div>
      </div>

      {/* Triage Overview Statistics Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-[10px] font-mono text-slate-400 uppercase block mb-1">TOTAL ACTIVE ALERTS</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{activeAlertsCount}</span>
            <span className="text-[10px] font-mono text-cyan-400">All Crew</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30">
          <span className="text-[10px] font-mono text-rose-300 uppercase block mb-1">CRITICAL INCIDENTS</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-rose-400">{criticalCount}</span>
            <span className="text-[10px] font-mono text-rose-400/80">Immediate Escalation</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
          <span className="text-[10px] font-mono text-amber-300 uppercase block mb-1">WARNING ADVISORIES</span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-amber-400">{warningCount}</span>
            <span className="text-[10px] font-mono text-amber-400/80">Closer Monitoring</span>
          </div>
        </div>

        {/* Integration Slot for Teammate's Z-Score Anomaly Engine */}
        <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-800/40 relative overflow-hidden group">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] font-mono text-purple-300 uppercase">TEAMMATE ANOMALY DOCK</span>
            <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-purple-900/60 text-purple-200 border border-purple-700/50">
              Palette 3
            </span>
          </div>
          <div className="text-xs text-purple-200/90 font-mono mt-0.5">
            Z-Score Anomaly Engine: <span className="text-purple-400 font-bold">READY TO DOCK</span>
          </div>
          <p className="text-[10px] text-purple-400/80 mt-1 font-mono">
            Clean integration interface prepared for Matthew's statistical models.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-xl p-4 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Status Tabs */}
        <div className="flex items-center p-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
          <button
            onClick={() => setActiveTab('ACTIVE')}
            className={`px-3 py-1.5 rounded transition ${
              activeTab === 'ACTIVE'
                ? 'bg-rose-950/80 text-rose-300 font-semibold border border-rose-500/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Active ({activeAlertsCount})
          </button>
          <button
            onClick={() => setActiveTab('RESOLVED')}
            className={`px-3 py-1.5 rounded transition ${
              activeTab === 'RESOLVED'
                ? 'bg-emerald-950/80 text-emerald-300 font-semibold border border-emerald-500/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Resolved ({alerts.filter((a) => a.status === 'RESOLVED').length})
          </button>
          <button
            onClick={() => setActiveTab('ALL')}
            className={`px-3 py-1.5 rounded transition ${
              activeTab === 'ALL'
                ? 'bg-slate-800 text-slate-200 font-semibold border border-slate-700'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All History ({alerts.length})
          </button>
        </div>

        {/* Severity Chips & Crew Checkbox */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Severity filter chips */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className="text-slate-400 text-[11px]">SEVERITY:</span>
            {['ALL', 'CRITICAL', 'WARNING', 'NO_DATA'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-2 py-1 rounded text-[11px] border transition ${
                  severityFilter === sev
                    ? 'bg-slate-800 border-cyan-500/50 text-cyan-300 font-semibold'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Toggle filter by active astronaut */}
          <label className="flex items-center gap-2 text-xs font-mono text-slate-300 cursor-pointer pl-2 border-l border-slate-800">
            <input
              type="checkbox"
              checked={filterBySelectedAstronautOnly}
              onChange={(e) => setFilterBySelectedAstronautOnly(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
            />
            <span>Selected Crew Only ({selectedAstronaut.id})</span>
          </label>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search alerts, rules, keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 w-full sm:w-60 font-mono"
          />
        </div>
      </div>

      {/* List of Triage Alerts */}
      <div className="space-y-3">
        {filteredAlerts.length > 0 ? (
          filteredAlerts.map((alert) => {
            const astro = astronauts.find((a) => a.id === alert.astronautId);
            const isCritical = alert.severity === 'CRITICAL';
            const isWarning = alert.severity === 'WARNING';

            return (
              <div
                key={alert.id}
                onClick={() => handleOpenAlert(alert)}
                className={`glass-card rounded-xl p-4 cursor-pointer transition border relative group ${
                  isCritical
                    ? 'border-rose-500/40 hover:border-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.1)]'
                    : isWarning
                    ? 'border-amber-500/40 hover:border-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.1)]'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-3 mb-2">
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg border shrink-0 mt-0.5 ${
                        isCritical
                          ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                          : isWarning
                          ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                          : 'bg-slate-800 border-slate-700 text-slate-400'
                      }`}
                    >
                      <ShieldAlert className="w-5 h-5" />
                    </div>

                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300 transition">
                          {alert.title}
                        </h4>
                        <span className="text-[10px] font-mono text-slate-400">
                          ID: {alert.id}
                        </span>
                        <span className="text-[10px] font-mono text-cyan-400/80">
                          {alert.ruleId}
                        </span>
                      </div>

                      {/* Astronaut & Timestamp line */}
                      <div className="flex items-center gap-3 text-xs font-mono text-slate-400 mb-2">
                        <span className="flex items-center gap-1 text-slate-300">
                          <User className="w-3 h-3 text-cyan-400" />
                          {astro?.name || alert.astronautId} ({alert.astronautId})
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          {alert.timestamp ? alert.timestamp.replace('T', ' ').substring(0, 16) + ' UTC' : '—'}
                        </span>
                      </div>

                      {/* Transparent Trigger Reason */}
                      <p className="text-xs text-slate-300 font-sans leading-relaxed">
                        {alert.triggerReason}
                      </p>
                    </div>
                  </div>

                  {/* Right side: Severity Badge & Details CTA */}
                  <div className="flex md:flex-col items-center md:items-end justify-between gap-2 shrink-0">
                    <SeverityBadge severity={alert.severity} size="md" />
                    <span className="text-[11px] font-mono text-cyan-400 group-hover:underline flex items-center gap-1">
                      View Clinical Details →
                    </span>
                  </div>
                </div>

                {/* Contributing measurements chips preview */}
                <div className="flex flex-wrap items-center gap-2 pt-3 mt-2 border-t border-slate-800/80">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">
                    CONTRIBUTING TELEMETRY:
                  </span>
                  {alert.contributingMeasurements?.map((m, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300"
                    >
                      <strong className="text-white">{m.name}:</strong> {m.value}{' '}
                      <span className="text-slate-400">({m.threshold})</span>
                    </span>
                  ))}
                </div>
              </div>
            );
          })
        ) : (
          <div className="glass-panel rounded-xl p-8 border border-slate-800 text-center">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-200">No Alerts Matching Criteria</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              All monitored physiological criteria are nominal for the current filter configuration.
            </p>
          </div>
        )}
      </div>

      {/* Alert Detail Modal */}
      <AlertDetailModal
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        alert={selectedAlert}
        astronaut={astronauts.find((a) => a.id === selectedAlert?.astronautId)}
        onAcknowledge={onAcknowledgeAlert}
      />

      {/* Rule Configuration Modal */}
      <RuleConfigModal
        isOpen={isConfigModalOpen}
        onClose={() => setIsConfigModalOpen(false)}
      />
    </div>
  );
}
