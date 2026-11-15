import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import WelcomeView from './components/views/WelcomeView';
import LoginView from './components/views/LoginView';
import AstronautDashboardView from './components/views/AstronautDashboardView';
import VitalsDashboard from './components/modules/Module1Vitals/VitalsDashboard';
import BodyMapViewer from './components/modules/Module2BodyMap/BodyMapViewer';
import TriageDashboard from './components/modules/Module3Triage/TriageDashboard';
import HealthHistoryView from './components/views/HealthHistoryView';
import MissionOverviewView from './components/views/MissionOverviewView';
import CrewManagementView from './components/views/CrewManagementView';
import TeammateIntegrationView from './components/views/TeammateIntegrationView';

import {
  getMissions,
  getAstronauts,
  getLatestHealth,
  getHealthHistory,
  postHealthReading,
  getAlerts,
  resolveAlert,
} from './services/api';

import {
  MISSIONS as FALLBACK_MISSIONS,
  ASTRONAUTS as FALLBACK_ASTRONAUTS,
  CURRENT_READINGS as FALLBACK_READINGS,
  TRIAGE_ALERTS as FALLBACK_ALERTS,
  generateHistoricalData,
} from './data/mockData';

export default function App() {
  const [appScreen, setAppScreen] = useState('welcome'); // 'welcome' | 'login' | 'authenticated'
  const [currentUser, setCurrentUser] = useState({
    id: 'ASTRO-001',
    name: 'Dr. Sarah Chen',
    role: 'Flight Surgeon',
    email: 'sarah.chen@starhealers.space',
    callsign: 'MED-SURGEON-01',
  });
  const [activeTab, setActiveTab] = useState('astronaut-dashboard');
  const [missions, setMissions] = useState(FALLBACK_MISSIONS);
  const [selectedMission, setSelectedMission] = useState(FALLBACK_MISSIONS[0]);
  const [astronauts, setAstronauts] = useState(FALLBACK_ASTRONAUTS);
  const [selectedAstronaut, setSelectedAstronaut] = useState(FALLBACK_ASTRONAUTS[0]);
  const [readingsState, setReadingsState] = useState(FALLBACK_READINGS);
  const [alertsState, setAlertsState] = useState(FALLBACK_ALERTS);
  const [timeRange, setTimeRange] = useState('24h');
  const [isLiveSimulating, setIsLiveSimulating] = useState(true);
  const [historicalData, setHistoricalData] = useState(() =>
    generateHistoricalData(FALLBACK_ASTRONAUTS[0].id, '24h')
  );
  const [backendConnected, setBackendConnected] = useState(false);

  // Load Initial Data from Backend
  useEffect(() => {
    async function loadInitialData() {
      try {
        const [fetchedMissions, fetchedAstronauts, fetchedAlerts] = await Promise.all([
          getMissions(),
          getAstronauts(),
          getAlerts(),
        ]);
        if (fetchedMissions && fetchedMissions.length > 0) setMissions(fetchedMissions);
        if (fetchedAstronauts && fetchedAstronauts.length > 0) {
          setAstronauts(fetchedAstronauts);
          setSelectedAstronaut(fetchedAstronauts[0]);
        }
        if (fetchedAlerts && fetchedAlerts.length > 0) setAlertsState(fetchedAlerts);
        setBackendConnected(true);
      } catch (err) {
        console.warn('Initial backend load failed, using local mock data.');
      }
    }
    loadInitialData();
  }, []);

  // Fetch Vitals & Telemetry when Selected Astronaut or TimeRange Changes
  const loadAstronautTelemetry = useCallback(async (astroId, range) => {
    try {
      const [vitals, history] = await Promise.all([
        getLatestHealth(astroId),
        getHealthHistory(astroId, range),
      ]);
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: vitals,
      }));
      if (history && history.length > 0) {
        setHistoricalData(history);
      }
    } catch (err) {
      console.warn(`Error loading telemetry for ${astroId}:`, err);
    }
  }, []);

  useEffect(() => {
    loadAstronautTelemetry(selectedAstronaut.id, timeRange);
  }, [selectedAstronaut.id, timeRange, loadAstronautTelemetry]);

  // Live Telemetry Simulation Loop (Module 1 Live Stream)
  useEffect(() => {
    if (!isLiveSimulating) return;

    const interval = setInterval(async () => {
      const astroId = selectedAstronaut.id;
      const current = readingsState[astroId];
      if (!current || !current.heartRate || current.heartRate.value === null) return;

      // Realistic micro-oscillation
      const hrDelta = Math.floor(Math.random() * 3) - 1; // -1, 0, +1
      const hrvDelta = Math.floor(Math.random() * 3) - 1;
      const newHr = Math.max(50, Math.min(130, current.heartRate.value + hrDelta));
      const newHrv = Math.max(20, Math.min(110, current.hrv.value + hrvDelta));
      const ts = new Date().toISOString();

      // Persist reading to backend database via REST API
      postHealthReading(astroId, {
        metric_name: 'heartRate',
        value: newHr,
        unit: 'bpm',
        source: 'SIMULATED',
        quality_status: 'GOOD',
        severity: current.heartRate.severity || 'NORMAL',
        timestamp: ts,
      });

      // Update state locally for instant responsiveness
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: {
          ...prev[astroId],
          heartRate: {
            ...prev[astroId].heartRate,
            value: newHr,
            timestamp: ts,
            source: 'SIMULATED',
          },
          hrv: {
            ...prev[astroId].hrv,
            value: newHrv,
            timestamp: ts,
            source: 'SIMULATED',
          },
        },
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [isLiveSimulating, selectedAstronaut.id, readingsState]);

  // Handle Scenario Injections for Hackathon Demonstration
  const handleInjectScenario = async (scenario) => {
    const astroId = selectedAstronaut.id;

    if (scenario === 'nominal') {
      const updatedReadings = {
        ...readingsState[astroId],
        heartRate: { value: 64, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
        hrv: { value: 74, unit: 'ms', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
        spo2: { value: 99, unit: '%', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
        temperature: { value: 36.6, unit: '°C', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
        stress: { value: 22, unit: 'pts', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
        sleep: { value: 7.8, unit: 'hrs', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'NORMAL', status: 'NORMAL' },
      };
      setReadingsState((prev) => ({ ...prev, [astroId]: updatedReadings }));
      setAstronauts((prev) =>
        prev.map((a) =>
          a.id === astroId
            ? {
                ...a,
                status: 'NORMAL',
                statusReason: 'Nominal physiological parameters verified',
                bodyRegionStatus: {
                  brain: 'NORMAL',
                  heart: 'NORMAL',
                  lungs: 'NORMAL',
                  musculoskeletal: 'NORMAL',
                  immune: 'NORMAL',
                  metabolic: 'NORMAL',
                },
              }
            : a
        )
      );
      setSelectedAstronaut((prev) => ({ ...prev, status: 'NORMAL' }));
    } else if (scenario === 'fatigue') {
      const updatedReadings = {
        ...readingsState[astroId],
        heartRate: { value: 96, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'WARNING', status: 'WARNING' },
        hrv: { value: 32, unit: 'ms', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'WARNING', status: 'WARNING' },
        sleep: { value: 4.5, unit: 'hrs', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'WARNING', status: 'WARNING' },
        stress: { value: 74, unit: 'pts', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'WARNING', status: 'WARNING' },
      };
      setReadingsState((prev) => ({ ...prev, [astroId]: updatedReadings }));
      setAstronauts((prev) =>
        prev.map((a) =>
          a.id === astroId
            ? {
                ...a,
                status: 'WARNING',
                statusReason: 'Multi-signal autonomic fatigue pattern detected',
                bodyRegionStatus: {
                  ...a.bodyRegionStatus,
                  brain: 'WARNING',
                  heart: 'WARNING',
                },
              }
            : a
        )
      );
      setSelectedAstronaut((prev) => ({ ...prev, status: 'WARNING' }));
    } else if (scenario === 'hypoxia') {
      const updatedReadings = {
        ...readingsState[astroId],
        spo2: { value: 89, unit: '%', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'CRITICAL', status: 'CRITICAL' },
        heartRate: { value: 114, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), severity: 'CRITICAL', status: 'CRITICAL' },
      };
      setReadingsState((prev) => ({ ...prev, [astroId]: updatedReadings }));
      setAstronauts((prev) =>
        prev.map((a) =>
          a.id === astroId
            ? {
                ...a,
                status: 'CRITICAL',
                statusReason: 'Acute arterial hypoxemia and compensatory tachycardia',
                bodyRegionStatus: {
                  ...a.bodyRegionStatus,
                  lungs: 'CRITICAL',
                  heart: 'CRITICAL',
                },
              }
            : a
        )
      );
      setSelectedAstronaut((prev) => ({ ...prev, status: 'CRITICAL' }));
    } else if (scenario === 'nodata') {
      const nullReadings = {
        heartRate: { value: null, unit: 'bpm', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        hrv: { value: null, unit: 'ms', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        bloodPressure: { systolic: null, diastolic: null, unit: 'mmHg', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        spo2: { value: null, unit: '%', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        temperature: { value: null, unit: '°C', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        glucose: { value: null, unit: 'mg/dL', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        sleep: { value: null, unit: 'hrs', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        hydration: { value: null, unit: '%', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
        stress: { value: null, unit: 'pts', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), severity: 'NO_DATA', status: 'NO_DATA' },
      };
      setReadingsState((prev) => ({ ...prev, [astroId]: nullReadings }));
      setAstronauts((prev) =>
        prev.map((a) =>
          a.id === astroId
            ? {
                ...a,
                status: 'NO_DATA',
                statusReason: 'Telemetry packet loss / Sensor node disconnected',
                bodyRegionStatus: {
                  brain: 'NO_DATA',
                  heart: 'NO_DATA',
                  lungs: 'NO_DATA',
                  musculoskeletal: 'NO_DATA',
                  immune: 'NO_DATA',
                  metabolic: 'NO_DATA',
                },
              }
            : a
        )
      );
      setSelectedAstronaut((prev) => ({ ...prev, status: 'NO_DATA' }));
    }
  };

  // Handle Alert Acknowledging (persisting to SQLite backend)
  const handleAcknowledgeAlert = async (alertId) => {
    await resolveAlert(alertId, 'USR-MED-01');
    setAlertsState((prev) =>
      prev.map((a) =>
        a.id === alertId
          ? {
              ...a,
              status: 'RESOLVED',
              acknowledgedBy: 'Medical Officer Suba (Local Console)',
            }
          : a
      )
    );
  };

  const activeAlertsCount = alertsState.filter((a) => a.status === 'ACTIVE').length;
  const currentReadings = readingsState[selectedAstronaut.id] || {};

  // Entry Experience Screen 1: Welcome & Landing
  if (appScreen === 'welcome') {
    return (
      <WelcomeView
        onEnter={() => setAppScreen('login')}
        onQuickDemo={() => {
          setCurrentUser({
            id: 'ASTRO-001',
            name: 'Dr. Sarah Chen',
            role: 'Flight Surgeon',
            email: 'sarah.chen@starhealers.space',
            callsign: 'MED-SURGEON-01',
          });
          setAppScreen('authenticated');
        }}
      />
    );
  }

  // Entry Experience Screen 2: Medical Officer Sign-In
  if (appScreen === 'login') {
    return (
      <LoginView
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          setAppScreen('authenticated');
        }}
        onBackToWelcome={() => setAppScreen('welcome')}
      />
    );
  }

  // Entry Experience Screen 3-5: Authenticated Aerospace Health Platform
  return (
    <div className="min-h-screen bg-[#060913] text-[#F8FAFC] flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation Bar */}
      <Navbar
        missions={missions}
        selectedMission={selectedMission}
        onSelectMission={setSelectedMission}
        astronauts={astronauts}
        selectedAstronaut={selectedAstronaut}
        onSelectAstronaut={setSelectedAstronaut}
        isLiveSimulating={isLiveSimulating}
        onToggleLiveSimulating={() => setIsLiveSimulating(!isLiveSimulating)}
        activeAlertsCount={activeAlertsCount}
        currentUser={currentUser}
        onSignOut={() => setAppScreen('welcome')}
      />

      {/* Main Layout: Fixed Sidebar + Scrollable Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          alertsCount={activeAlertsCount}
          currentUser={currentUser}
          onSignOut={() => setAppScreen('welcome')}
        />

        {/* Dynamic Workspace Canvas */}
        <main className="flex-1 p-4 lg:p-6 overflow-y-auto max-h-[calc(100vh-57px)]">
          {activeTab === 'astronaut-dashboard' && (
            <AstronautDashboardView
              astronaut={selectedAstronaut}
              mission={selectedMission}
              readings={currentReadings}
              historicalData={historicalData}
              alerts={alertsState}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'vitals-monitoring' && (
            <VitalsDashboard
              astronaut={selectedAstronaut}
              readings={currentReadings}
              historicalData={historicalData}
              timeRange={timeRange}
              onChangeTimeRange={setTimeRange}
              isLiveSimulating={isLiveSimulating}
              onToggleLiveSimulating={() => setIsLiveSimulating(!isLiveSimulating)}
              onInjectScenario={handleInjectScenario}
            />
          )}

          {activeTab === 'body-map' && (
            <BodyMapViewer
              astronaut={selectedAstronaut}
              readings={currentReadings}
              alerts={alertsState}
              onNavigateToMetric={() => setActiveTab('vitals-monitoring')}
            />
          )}

          {activeTab === 'triage-alerts' && (
            <TriageDashboard
              alerts={alertsState}
              astronauts={astronauts}
              selectedAstronaut={selectedAstronaut}
              onSelectAstronaut={setSelectedAstronaut}
              onAcknowledgeAlert={handleAcknowledgeAlert}
            />
          )}

          {activeTab === 'health-history' && (
            <HealthHistoryView
              astronaut={selectedAstronaut}
              historicalData={historicalData}
              timeRange={timeRange}
              onChangeTimeRange={setTimeRange}
            />
          )}

          {activeTab === 'mission-overview' && (
            <MissionOverviewView
              missions={missions}
              selectedMission={selectedMission}
              onSelectMission={setSelectedMission}
              astronauts={astronauts}
              onSelectAstronaut={setSelectedAstronaut}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'crew-management' && (
            <CrewManagementView
              astronauts={astronauts}
              selectedAstronaut={selectedAstronaut}
              onSelectAstronaut={setSelectedAstronaut}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'teammate-integrations' && (
            <TeammateIntegrationView />
          )}
        </main>
      </div>
    </div>
  );
}
