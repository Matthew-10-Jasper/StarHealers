import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/apiClient';
import { ASTRONAUTS_FALLBACK } from '../data/mockData';

export type ActiveModuleId =
  | 'OVERVIEW'
  | 'MODULE_1'
  | 'MODULE_2'
  | 'MODULE_3'
  | 'MODULE_4'
  | 'MODULE_5'
  | 'MODULE_6'
  | 'MODULE_7'
  | 'SYSTEM_HEALTH';

export interface AstronautItem {
  id: string;
  name: string;
  role: string;
  callsign?: string;
  status: string;
  avatar?: string;
  missionId?: string;
  missionName?: string;
}

interface SharedMissionContextType {
  activeModule: ActiveModuleId;
  setActiveModule: (module: ActiveModuleId) => void;
  selectedAstronautId: string;
  setSelectedAstronautId: (id: string) => void;
  selectedMissionId: string;
  setSelectedMissionId: (id: string) => void;
  astronauts: AstronautItem[];
  selectedAstronaut: AstronautItem;
  systemHealth: any | null;
  isLoading: boolean;
  refreshAll: () => Promise<void>;
}

const SharedMissionContext = createContext<SharedMissionContextType | undefined>(undefined);

export const SharedMissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeModule, setActiveModule] = useState<ActiveModuleId>('OVERVIEW');
  const [selectedAstronautId, setSelectedAstronautId] = useState<string>('ASTRO-01');
  const [selectedMissionId, setSelectedMissionId] = useState<string>('ISS_EXPEDITION_LEO');
  const [astronauts, setAstronauts] = useState<AstronautItem[]>(ASTRONAUTS_FALLBACK);
  const [systemHealth, setSystemHealth] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const refreshAll = useCallback(async () => {
    try {
      setIsLoading(true);
      const [health, astros] = await Promise.allSettled([
        apiClient.getSystemHealth(),
        apiClient.getAstronauts(),
      ]);

      if (health.status === 'fulfilled') {
        setSystemHealth(health.value);
      }
      if (astros.status === 'fulfilled' && Array.isArray(astros.value) && astros.value.length > 0) {
        setAstronauts(
          astros.value.map((a: any) => ({
            id: a.astronaut_id || a.id,
            name: a.name,
            role: a.role,
            callsign: a.callsign || '',
            status: a.status || 'NORMAL',
            avatar:
              a.avatar ||
              ASTRONAUTS_FALLBACK.find((fb) => fb.id === (a.astronaut_id || a.id))?.avatar ||
              'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
            missionId: a.mission_id || a.missionId,
            missionName: a.mission_name || a.missionName,
          }))
        );
      }
    } catch (e) {
      console.warn('[SharedMissionProvider] Failed to fetch remote telemetry:', e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const selectedAstronaut =
    astronauts.find((a) => a.id === selectedAstronautId) ||
    ASTRONAUTS_FALLBACK.find((a) => a.id === selectedAstronautId) ||
    astronauts[0] ||
    ASTRONAUTS_FALLBACK[0];

  return (
    <SharedMissionContext.Provider
      value={{
        activeModule,
        setActiveModule,
        selectedAstronautId,
        setSelectedAstronautId,
        selectedMissionId,
        setSelectedMissionId,
        astronauts,
        selectedAstronaut,
        systemHealth,
        isLoading,
        refreshAll,
      }}
    >
      {children}
    </SharedMissionContext.Provider>
  );
};

export const useSharedMission = (): SharedMissionContextType => {
  const context = useContext(SharedMissionContext);
  if (!context) {
    throw new Error('useSharedMission must be used within a SharedMissionProvider');
  }
  return context;
};
