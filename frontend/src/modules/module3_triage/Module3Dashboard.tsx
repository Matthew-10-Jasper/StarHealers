import React, { useState, useEffect, useCallback } from 'react';
import { useSharedMission } from '../../context/SharedMissionContext';
import { apiClient } from '../../services/apiClient';
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
  Sparkles,
  RefreshCw,
  X,
} from 'lucide-react';

export const Module3Dashboard: React.FC = () => {
  const { selectedAstronaut } = useSharedMission();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'ACTIVE' | 'RESOLVED' | 'ALL'>('ACTIVE');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedAlert, setSelectedAlert] = useState<any | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState<boolean>(false);
  const [isRulesOpen, setIsRulesOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [filterCurrentAstroOnly, setFilterCurrentAstroOnly] = useState<boolean>(false);
  const [resolutionNote, setResolutionNote] = useState<string>('');

  const loadAlerts = useCallback(async () => {
    try {
      setIsLoading(true);
      const [fetchedAlerts, fetchedRules] = await Promise.allSettled([
        apiClient.getAlerts(),
        apiClient.getTriageRules(),
      ]);

      if (fetchedAlerts.status === 'fulfilled' && Array.isArray(fetchedAlerts.value)) {
        setAlerts(fetchedAlerts.value);
      } else {
        // Fallback demonstration alerts
        setAlerts([
          {
            id: 'ALT-101',
            astronautId: 'ASTRO-01',
            title: 'Sustained Tachycardia During EVA Pre-Breathe',
            severity: 'CRITICAL',
            status: 'ACTIVE',
            timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
            triggerReason: 'Heart rate exceeded 130 bpm for > 15 consecutive minutes (138 bpm current).',
            recommendedAction: 'Suspend hyperbaric pre-breathe protocol. Administer supplemental hydration and notify Flight Surgeon.',
            vitalTrigger: 'heartRate = 138 bpm (threshold: 130 bpm)',
            clinicalProtocol: 'NASA-STD-3001-V1-TACH-04',
          },
          {
            id: 'ALT-102',
            astronautId: 'ASTRO-01',
            title: 'Autonomic HRV Depletion & Acute Strain',
            severity: 'WARNING',
            status: 'ACTIVE',
            timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
            triggerReason: 'rMSSD dropped below 22 ms indicating parasympathetic withdrawal.',
            recommendedAction: 'Schedule mandatory 2-hour sleep buffer and restrict non-critical task list.',
            vitalTrigger: 'hrv = 21 ms (threshold: 25 ms)',
            clinicalProtocol: 'MED-RULE-HRV-02',
          },
          {
            id: 'ALT-103',
            astronautId: 'ASTRO-02',
            title: 'Transient Mild Hypoxia',
            severity: 'WARNING',
            status: 'RESOLVED',
            timestamp: new Date(Date.now() - 1000 * 60 * 600).toISOString(),
            triggerReason: 'SpO2 transiently dipped to 92.4% during exercise cycle.',
            recommendedAction: 'Adjust ergometer resistance and verify face mask seal.',
            vitalTrigger: 'spo2 = 92.4%',
            clinicalProtocol: 'EXERCISE-HYPOX-01',
          },
        ]);
      }

      if (fetchedRules.status === 'fulfilled' && Array.isArray(fetchedRules.value)) {
        setRules(fetchedRules.value);
      }
    } catch (e) {
      console.warn('[Module3] Error loading triage alerts:', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleResolveAlert = async (alertId: string) => {
    try {
      setIsLoading(true);
      await apiClient.resolveAlert(
        alertId,
        resolutionNote || 'Verified and resolved by Flight Medical Officer',
        'FLIGHT_SURGEON'
      );
      setIsDetailOpen(false);
      setResolutionNote('');
      await loadAlerts();
    } catch (e: any) {
      alert(`Could not resolve alert: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAlerts = alerts.filter((alert) => {
    const astroId = alert.astronaut_id || alert.astronautId;
    if (filterCurrentAstroOnly && astroId !== selectedAstronaut.id) return false;
    if (activeTab !== 'ALL' && alert.status !== activeTab) return false;
    if (severityFilter !== 'ALL' && alert.severity !== severityFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = (alert.title || '').toLowerCase().includes(q);
      const matchReason = (alert.trigger_reason || alert.triggerReason || '').toLowerCase().includes(q);
      const matchAstro = (astroId || '').toLowerCase().includes(q);
      if (!matchTitle && !matchReason && !matchAstro) return false;
    }
    return true;
  });

  const getSeverityStyle = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-950/70 border-rose-500 text-rose-300';
      case 'WARNING':
        return 'bg-amber-950/70 border-amber-500 text-amber-300';
      case 'NORMAL':
      default:
        return 'bg-emerald-950/70 border-emerald-500 text-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-5 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
            <h2 className="text-lg font-bold text-[#F8FAFC]">Module 3 • Autonomous Medical Triage & Protocol Advisor</h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/80 text-rose-300 border border-rose-800/40">
              NASA-STD-3001 ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Real-time automated clinical rule evaluator for deep space health emergencies.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsRulesOpen(true)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-700 text-slate-300 hover:text-white"
          >
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span>VIEW FLIGHT RULES</span>
          </button>
          <button
            onClick={loadAlerts}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-700 text-slate-300 hover:text-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-rose-400' : ''}`} />
            <span>SYNC</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#0F172A]/80 border border-[#1E293B] rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Status Tabs */}
        <div className="flex items-center space-x-1.5 bg-[#060913] p-1 rounded-lg border border-[#1E293B]">
          {(['ACTIVE', 'RESOLVED', 'ALL'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1 rounded text-xs font-mono font-bold transition ${
                activeTab === tab
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/50'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Severity & Astronaut Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-1 text-xs font-mono">
            <span className="text-slate-400">SEVERITY:</span>
            {['ALL', 'CRITICAL', 'WARNING'].map((s) => (
              <button
                key={s}
                onClick={() => setSeverityFilter(s)}
                className={`px-2 py-0.5 rounded text-[11px] ${
                  severityFilter === s ? 'bg-slate-700 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <label className="flex items-center space-x-1.5 text-xs font-mono text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={filterCurrentAstroOnly}
              onChange={(e) => setFilterCurrentAstroOnly(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-rose-500 focus:ring-rose-500"
            />
            <span>{selectedAstronaut.id} ONLY</span>
          </label>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              placeholder="Search alerts or symptoms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-700 rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 w-56"
            />
          </div>
        </div>
      </div>

      {/* Alerts Grid */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="bg-[#0F172A]/40 border border-[#1E293B] rounded-xl p-8 text-center">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-slate-300">No triage alerts match current filter criteria.</p>
            <p className="text-xs text-slate-500 font-mono mt-1">Astronaut health states within safe bounds.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const astroId = alert.astronaut_id || alert.astronautId;
            const title = alert.title;
            const reason = alert.trigger_reason || alert.triggerReason;
            const recAction = alert.recommended_action || alert.recommendedAction;
            const sev = alert.severity;
            const status = alert.status;

            return (
              <div
                key={alert.id}
                onClick={() => {
                  setSelectedAlert(alert);
                  setIsDetailOpen(true);
                }}
                className="bg-[#0F172A]/80 border border-[#1E293B] hover:border-slate-700 rounded-xl p-4 cursor-pointer transition flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg border mt-0.5 ${getSeverityStyle(sev)}`}>
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-slate-300">[{astroId}]</span>
                      <h4 className="text-sm font-bold text-white">{title}</h4>
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${getSeverityStyle(sev)}`}>
                        {sev}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        {status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-1">
                      {reason}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 shrink-0 self-end md:self-center">
                  <div className="text-right">
                    <div className="text-[10px] font-mono text-slate-500 flex items-center justify-end space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(alert.timestamp || alert.created_at || Date.now()).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-[11px] font-mono text-rose-400 font-semibold mt-0.5">
                      Protocol: {alert.clinical_protocol || alert.clinicalProtocol || 'NASA-STD-3001'}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Alert Detail Modal */}
      {isDetailOpen && selectedAlert && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-slate-700 rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${getSeverityStyle(selectedAlert.severity)}`}>
                  {selectedAlert.severity}
                </span>
                <h3 className="text-base font-bold text-white">{selectedAlert.title}</h3>
              </div>
              <button
                onClick={() => setIsDetailOpen(false)}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="font-mono text-slate-400">AFFECTED ASTRONAUT:</span>
                <div className="text-sm font-semibold text-white mt-0.5">
                  {selectedAlert.astronaut_id || selectedAlert.astronautId}
                </div>
              </div>

              <div>
                <span className="font-mono text-slate-400">TRIGGER REASON & PHYSIOLOGICAL JUSTIFICATION:</span>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 mt-1 font-mono">
                  {selectedAlert.trigger_reason || selectedAlert.triggerReason}
                </div>
              </div>

              <div>
                <span className="font-mono text-slate-400">RECOMMENDED CLINICAL PROTOCOL (NASA-STD-3001):</span>
                <div className="p-3 bg-emerald-950/30 border border-emerald-500/40 rounded-lg text-emerald-300 mt-1 font-sans leading-relaxed">
                  {selectedAlert.recommended_action || selectedAlert.recommendedAction}
                </div>
              </div>

              {selectedAlert.status === 'ACTIVE' && (
                <div className="pt-2">
                  <label className="block text-xs font-mono text-slate-400 mb-1">
                    CLINICAL RESOLUTION ACTION NOTE:
                  </label>
                  <textarea
                    rows={2}
                    value={resolutionNote}
                    onChange={(e) => setResolutionNote(e.target.value)}
                    placeholder="Describe clinical actions taken to stabilize crew member..."
                    className="w-full p-2 bg-slate-900 border border-slate-700 rounded text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-emerald-500"
                  />
                  <div className="flex justify-end space-x-2 mt-3">
                    <button
                      onClick={() => setIsDetailOpen(false)}
                      className="px-3 py-1.5 rounded text-xs font-mono text-slate-400 hover:text-white"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleResolveAlert(selectedAlert.id)}
                      disabled={isLoading}
                      className="px-4 py-1.5 rounded text-xs font-mono font-bold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center space-x-1.5 transition"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span>AUTHORIZE RESOLUTION</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rules Modal */}
      {isRulesOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F172A] border border-slate-700 rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <Sliders className="w-5 h-5 text-amber-400" />
                <span>Active Clinical Triage & Flight Rules</span>
              </h3>
              <button
                onClick={() => setIsRulesOpen(false)}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              {[
                { name: 'Sustained Tachycardia', param: 'heartRate > 130 bpm', duration: '15 min', severity: 'CRITICAL' },
                { name: 'Autonomic Exhaustion', param: 'hrv < 25 ms', duration: '30 min', severity: 'WARNING' },
                { name: 'Peripheral Hypoxia', param: 'spo2 < 90%', duration: '2 min', severity: 'CRITICAL' },
                { name: 'Hyperthermia / Fever', param: 'temp > 38.5 °C', duration: 'Immediate', severity: 'CRITICAL' },
                { name: 'Severe Sleep Debt', param: 'sleep < 4.5 h / day', duration: '3 days', severity: 'WARNING' },
              ].map((r, i) => (
                <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold text-white">{r.name}</div>
                    <div className="text-[11px] font-mono text-slate-400 mt-0.5">
                      Trigger: <span className="text-amber-300">{r.param}</span> ({r.duration})
                    </div>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${getSeverityStyle(r.severity)}`}>
                    {r.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
