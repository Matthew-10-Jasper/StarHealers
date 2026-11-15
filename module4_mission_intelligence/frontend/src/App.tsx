import React, { useEffect, useState, useCallback } from 'react';
import { api, TelemetryWebSocket } from './services/api';
import { MissionContextResponse, MissionProfile, MissionHistoryResponse, OperationalState } from './types/mission';
import { parseMissionContext } from './schemas/contracts';
import { Header, ActiveModuleType } from './components/Header';
import { Module6Dashboard } from './components/module6/Module6Dashboard';
import { Module7Dashboard } from './components/module7/Module7Dashboard';
import { MissionOverview } from './components/MissionOverview';
import { PlannedVsActual } from './components/PlannedVsActual';
import { OperationalStatePanel } from './components/OperationalStatePanel';
import { DeviationMonitor } from './components/DeviationMonitor';
import { EnvironmentMonitor } from './components/EnvironmentMonitor';
import { CommunicationMonitor } from './components/CommunicationMonitor';
import { MissionTimeline } from './components/MissionTimeline';
import { ProfileSelector } from './components/ProfileSelector';
import { SimulatorControls } from './components/SimulatorControls';
import { IntegrationInspector } from './components/IntegrationInspector';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [context, setContext] = useState<MissionContextResponse | null>(null);
  const [profiles, setProfiles] = useState<MissionProfile[]>([]);
  const [history, setHistory] = useState<MissionHistoryResponse>({ audit_events: [], state_transitions: [] });
  const [wsConnected, setWsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeModule, setActiveModule] = useState<ActiveModuleType>('MODULE_4');

  const activeProfile = profiles.find((p) => p.mission_id === context?.planned_profile);

  const loadInitialData = useCallback(async () => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const [currentCtx, allProfiles, hist] = await Promise.all([
        api.getCurrentMission(),
        api.getMissions(),
        api.getHistory()
      ]);
      setContext(parseMissionContext(currentCtx));
      setProfiles(allProfiles);
      setHistory(hist);
    } catch (err: any) {
      console.error('Failed to load initial mission data:', err);
      setErrorMessage(err.message || 'Could not connect to Mission Intelligence API. Ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInitialData();

    // Setup live WebSocket stream
    const ws = new TelemetryWebSocket(
      (data) => {
        if (data.context) {
          setContext(parseMissionContext(data.context));
        }
      },
      (connected) => {
        setWsConnected(connected);
      }
    );
    ws.connect();

    // Fallback polling every 5s
    const pollInterval = setInterval(async () => {
      try {
        const [c, h] = await Promise.all([api.getCurrentMission(), api.getHistory()]);
        setContext(c);
        setHistory(h);
      } catch (e) {
        // quiet error during background poll
      }
    }, 5000);

    return () => {
      ws.disconnect();
      clearInterval(pollInterval);
    };
  }, [loadInitialData]);

  const handleSelectMission = async (missionId: string) => {
    try {
      setIsLoading(true);
      const updated = await api.selectMission(missionId);
      setContext(updated);
      const h = await api.getHistory();
      setHistory(h);
    } catch (e: any) {
      alert('Failed to switch mission profile: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStateTransition = async (targetState: OperationalState, reason: string, evidence?: Record<string, any>) => {
    const updated = await api.requestStateTransition(targetState, reason, evidence);
    setContext(updated);
    const h = await api.getHistory();
    setHistory(h);
  };

  const handleTriggerScenario = async (scenario: string) => {
    try {
      setIsLoading(true);
      await api.runScenario(scenario);
      const [c, h] = await Promise.all([api.getCurrentMission(), api.getHistory()]);
      setContext(c);
      setHistory(h);
    } catch (e: any) {
      alert('Scenario trigger failed: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateStream = async () => {
    try {
      setIsLoading(true);
      await api.generateTelemetryStream();
      const [c, h] = await Promise.all([api.getCurrentMission(), api.getHistory()]);
      setContext(c);
      setHistory(h);
    } catch (e: any) {
      alert('Stream generation failed: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangePhase = async (phase: string) => {
    try {
      setIsLoading(true);
      const updated = await api.updateContext(phase, 'Manual flight phase divergence injection', { source: 'SIMULATOR_OVERRIDE' });
      setContext(updated);
      const h = await api.getHistory();
      setHistory(h);
    } catch (e: any) {
      alert('Phase change failed: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060913] text-[#F8FAFC] flex flex-col font-sans selection:bg-crimson-500/30 selection:text-white pb-12">
      {/* Header */}
      {context && (
        <Header
          operationalState={context.operational_state}
          missionName={activeProfile?.mission_name || context.mission_id}
          contextVersion={context.context_version}
          dataQuality={context.data_quality.overall_status}
          wsConnected={wsConnected}
          onRefresh={loadInitialData}
          isLoading={isLoading}
          activeModule={activeModule}
          onSelectModule={setActiveModule}
        />
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 w-full mt-6 space-y-6">
        {errorMessage && (
          <div className="p-4 rounded-xl bg-crimson-950/60 border border-crimson-500/60 flex items-start space-x-3 text-crimson-200">
            <AlertCircle className="h-5 w-5 text-crimson-400 shrink-0 mt-0.5" />
            <div className="text-xs font-mono">
              <span className="font-bold">CONNECTION ERROR: </span>
              {errorMessage}
              <button
                onClick={loadInitialData}
                className="ml-4 underline hover:text-white font-semibold"
              >
                Retry Handshake
              </button>
            </div>
          </div>
        )}

        {context ? (
          activeModule === 'MODULE_6' ? (
            <Module6Dashboard />
          ) : activeModule === 'MODULE_7' ? (
            <Module7Dashboard />
          ) : (
            <>
              {/* Section A: Mission Overview */}
              <MissionOverview context={context} profile={activeProfile} />

              {/* Section B: Planned vs Actual Environment Differential Matrix */}
              <PlannedVsActual context={context} profile={activeProfile} />

              {/* Section C: Operational State Panel */}
              <OperationalStatePanel
                currentState={context.operational_state}
                onTransition={handleStateTransition}
                isLoading={isLoading}
              />

              {/* Grid: Section D & Section F */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-7">
                  {/* Section D: Active Deviations Monitor */}
                  <DeviationMonitor deviations={context.active_deviations} />
                </div>
                <div className="lg:col-span-5">
                  {/* Section F: Communication & Autonomy Constraints */}
                  <CommunicationMonitor communication={context.communication} />
                </div>
              </div>

              {/* Section E: Environment Monitor with Historical Charting */}
              <EnvironmentMonitor environment={context.environment} dataQuality={context.data_quality} />

              {/* Section I: Development Telemetry Simulator */}
              <SimulatorControls
                onTriggerScenario={handleTriggerScenario}
                onGenerateStream={handleGenerateStream}
                onChangePhase={handleChangePhase}
                isLoading={isLoading}
              />

              {/* Section H: Mission Profile Selector */}
              <ProfileSelector
                profiles={profiles}
                activeMissionId={context.mission_id}
                onSelectMission={handleSelectMission}
                isLoading={isLoading}
              />

              {/* Section G: Mission Timeline and Audit Ledger */}
              <MissionTimeline history={history} />

              {/* Section J: Integration Inspector */}
              <IntegrationInspector />
            </>
          )
        ) : (
          <div className="py-24 flex flex-col items-center justify-center space-y-3">
            <RefreshCw className="h-8 w-8 text-amber-400 animate-spin" />
            <p className="text-sm font-mono text-slate-400">
              Initializing Spacecraft Telemetry Pipeline...
            </p>
          </div>
        )}
      </main>
    </div>
  );
};
export default App;

