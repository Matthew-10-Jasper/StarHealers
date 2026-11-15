import React, { useState, useEffect } from 'react';
import Navbar from './components/common/Navbar';
import Sidebar from './components/common/Sidebar';
import AstronautDashboardView from './components/views/AstronautDashboardView';
import VitalsDashboard from './components/modules/Module1Vitals/VitalsDashboard';
import BodyMapViewer from './components/modules/Module2BodyMap/BodyMapViewer';
import TriageDashboard from './components/modules/Module3Triage/TriageDashboard';
import HealthHistoryView from './components/views/HealthHistoryView';
import MissionOverviewView from './components/views/MissionOverviewView';
import CrewManagementView from './components/views/CrewManagementView';
import TeammateIntegrationView from './components/views/TeammateIntegrationView';

import {
  MISSIONS,
  ASTRONAUTS,
  CURRENT_READINGS,
  TRIAGE_ALERTS,
  generateHistoricalData,
} from './data/mockData';

export default function App() {
  const [activeTab, setActiveTab] = useState('astronaut-dashboard');
  const [selectedMission, setSelectedMission] = useState(MISSIONS[0]); // Mars Transit
  const [astronauts, setAstronauts] = useState(ASTRONAUTS);
  const [selectedAstronaut, setSelectedAstronaut] = useState(ASTRONAUTS[0]); // Dr. Sarah Chen
  const [readingsState, setReadingsState] = useState(CURRENT_READINGS);
  const [alertsState, setAlertsState] = useState(TRIAGE_ALERTS);
  const [timeRange, setTimeRange] = useState('24h');
  const [isLiveSimulating, setIsLiveSimulating] = useState(true);
  const [historicalData, setHistoricalData] = useState(() =>
    generateHistoricalData(ASTRONAUTS[0].id, '24h')
  );

  // Update historical data when astronaut or time range changes
  useEffect(() => {
    setHistoricalData(generateHistoricalData(selectedAstronaut.id, timeRange));
  }, [selectedAstronaut.id, timeRange]);

  // Live telemetry simulation ticker
  useEffect(() => {
    if (!isLiveSimulating) return;

    const interval = setInterval(() => {
      setReadingsState((prev) => {
        const astroId = selectedAstronaut.id;
        const current = prev[astroId];
        if (!current || current.heartRate.value === null) return prev;

        // Apply gentle physiological micro-oscillation
        const hrDelta = Math.floor(Math.random() * 3) - 1; // -1, 0, or +1
        const hrvDelta = Math.floor(Math.random() * 3) - 1;
        const newHr = Math.max(50, Math.min(130, current.heartRate.value + hrDelta));
        const newHrv = Math.max(20, Math.min(110, current.hrv.value + hrvDelta));

        return {
          ...prev,
          [astroId]: {
            ...current,
            heartRate: {
              ...current.heartRate,
              value: newHr,
              timestamp: new Date().toISOString(),
              source: 'SIMULATED',
            },
            hrv: {
              ...current.hrv,
              value: newHrv,
              timestamp: new Date().toISOString(),
              source: 'SIMULATED',
            },
          },
        };
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [isLiveSimulating, selectedAstronaut.id]);

  // Handle Scenario Injections for Demonstrations
  const handleInjectScenario = (scenario) => {
    const astroId = selectedAstronaut.id;

    if (scenario === 'nominal') {
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: {
          ...prev[astroId],
          heartRate: { value: 64, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
          hrv: { value: 72, unit: 'ms', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
          spo2: { value: 99, unit: '%', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
          temperature: { value: 36.6, unit: '°C', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
          stress: { value: 22, unit: 'pts', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
          sleep: { value: 7.8, unit: 'hrs', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'NORMAL' },
        },
      }));
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
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: {
          ...prev[astroId],
          heartRate: { value: 96, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'WARNING' },
          hrv: { value: 32, unit: 'ms', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'WARNING' },
          sleep: { value: 4.5, unit: 'hrs', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'WARNING' },
          stress: { value: 74, unit: 'pts', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'WARNING' },
        },
      }));
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
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: {
          ...prev[astroId],
          spo2: { value: 89, unit: '%', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'CRITICAL' },
          heartRate: { value: 114, unit: 'bpm', source: 'SIMULATED', quality: 'GOOD', timestamp: new Date().toISOString(), status: 'CRITICAL' },
        },
      }));
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
      setReadingsState((prev) => ({
        ...prev,
        [astroId]: {
          heartRate: { value: null, unit: 'bpm', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          hrv: { value: null, unit: 'ms', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          bloodPressure: { systolic: null, diastolic: null, unit: 'mmHg', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          spo2: { value: null, unit: '%', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          temperature: { value: null, unit: '°C', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          glucose: { value: null, unit: 'mg/dL', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          sleep: { value: null, unit: 'hrs', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          hydration: { value: null, unit: '%', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
          stress: { value: null, unit: 'pts', source: 'SIMULATED', quality: 'UNAVAILABLE', timestamp: new Date().toISOString(), status: 'NO_DATA' },
        },
      }));
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

  // Handle Alert Acknowledging
  const handleAcknowledgeAlert = (alertId) => {
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

  return (
    <div className="min-h-screen bg-[#060913] text-[#F8FAFC] flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Mission Control Navigation Bar */}
      <Navbar
        missions={MISSIONS}
        selectedMission={selectedMission}
        onSelectMission={setSelectedMission}
        astronauts={astronauts}
        selectedAstronaut={selectedAstronaut}
        onSelectAstronaut={setSelectedAstronaut}
        isLiveSimulating={isLiveSimulating}
        onToggleLiveSimulating={() => setIsLiveSimulating(!isLiveSimulating)}
        activeAlertsCount={activeAlertsCount}
      />

      {/* Main Layout: Fixed Sidebar + Scrollable Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          alertsCount={activeAlertsCount}
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
              missions={MISSIONS}
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
