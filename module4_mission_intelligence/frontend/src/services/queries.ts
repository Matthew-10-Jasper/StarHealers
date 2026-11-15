import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from './api';
import { parseMissionContext } from '../schemas/contracts';
import { OperationalState } from '../types/mission';

export const MISSION_KEYS = {
  current: ['mission', 'current'] as const,
  profiles: ['mission', 'profiles'] as const,
  deviations: ['mission', 'deviations'] as const,
  history: (limit: number, offset: number) => ['mission', 'history', limit, offset] as const,
  anomalies: ['mission', 'anomalies'] as const,
};

export function useCurrentMission() {
  return useQuery({
    queryKey: MISSION_KEYS.current,
    queryFn: async () => {
      const raw = await api.getCurrentMission();
      return parseMissionContext(raw);
    },
    refetchInterval: 3000,
  });
}

export function useMissionProfiles() {
  return useQuery({
    queryKey: MISSION_KEYS.profiles,
    queryFn: () => api.getMissions(),
    staleTime: 60000,
  });
}

export function useMissionDeviations() {
  return useQuery({
    queryKey: MISSION_KEYS.deviations,
    queryFn: () => api.getDeviations(),
    refetchInterval: 3000,
  });
}

export function useMissionHistory(limit = 50, offset = 0) {
  return useQuery({
    queryKey: MISSION_KEYS.history(limit, offset),
    queryFn: () => api.getHistory(undefined, limit, offset),
  });
}

export function useMissionAnomalies() {
  return useQuery({
    queryKey: MISSION_KEYS.anomalies,
    queryFn: async () => {
      const res = await fetch('http://localhost:8004/missions/anomalies/detect');
      if (!res.ok) throw new Error('Failed to query anomaly detector');
      return res.json();
    },
    refetchInterval: 5000,
  });
}

export function useTransitionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      targetState,
      reason,
      evidence,
    }: {
      targetState: OperationalState;
      reason: string;
      evidence?: Record<string, any>;
    }) => api.requestStateTransition(targetState, reason, evidence || {}),
    onSuccess: (updatedContext) => {
      queryClient.setQueryData(MISSION_KEYS.current, parseMissionContext(updatedContext));
      queryClient.invalidateQueries({ queryKey: MISSION_KEYS.deviations });
      queryClient.invalidateQueries({ queryKey: ['mission', 'history'] });
    },
  });
}

